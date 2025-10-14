import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Alert } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { retiroSinTarjetaService, tarjetaService, transaccionService, cajeroService } from '../services/api';

function Cajero() {
  const [currentScreen, setCurrentScreen] = useState('main'); // main, cajeroSelection, cardInserted, pinEntry, menu, retiro, retiroSinTarjeta, processing
  const [cardData, setCardData] = useState({ numero: '', pin: '' });
  const [retiroData, setRetiroData] = useState({ monto: 0, imprimirBoucher: false });
  const [retiroSinTarjeta, setRetiroSinTarjeta] = useState({ 
    numero_celular: '', 
    monto: '', 
    codigo: '',
    intentos: 0  // Agregar contador de intentos local
  });
  const [processingStep, setProcessingStep] = useState('');
  const [processingMessage, setProcessingMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [cajeros, setCajeros] = useState([]);
  const [cajerosLoading, setCajerosLoading] = useState(true);
  const [cajeroSeleccionado, setCajeroSeleccionado] = useState(null);

  // Detectar tecla 'T' para insertar tarjeta
  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.key.toLowerCase() === 't' && currentScreen === 'main') {
        setCurrentScreen('cajeroSelection');
        toast.info('Tarjeta insertada. Seleccione el cajero.');
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentScreen]);

  // Cargar cajeros disponibles
  useEffect(() => {
    const cargarCajeros = async () => {
      setCajerosLoading(true);
      try {
        const response = await cajeroService.listar();
        console.log('Cajeros cargados:', response.data); // Debug para ver los datos
        const cajerosActivos = response.data.filter(cajero => 
          cajero.caj_estado === 'Activo' || cajero.caj_estado === 'ACTIVO'
        );
        setCajeros(cajerosActivos);
        console.log('Cajeros activos filtrados:', cajerosActivos); // Debug
        // No seleccionar automáticamente, dejar que el usuario seleccione
      } catch (error) {
        console.error('Error al cargar cajeros:', error);
        toast.error('Error al cargar información de cajeros');
      } finally {
        setCajerosLoading(false);
      }
    };

    cargarCajeros();
  }, []);

  const handleCajeroSelection = (cajeroId) => {
    setCajeroSeleccionado(cajeroId);
    setCurrentScreen('cardInserted');
    const cajeroSeleccionadoInfo = cajeros.find(c => c.caj_id === cajeroId);
    toast.success(`Cajero seleccionado: ${cajeroSeleccionadoInfo?.caj_ubicacion}. Ingrese sus datos.`);
  };

  const handlePinSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (cardData.pin.length !== 4) {
        toast.error('El PIN debe tener 4 dígitos');
        setLoading(false);
        return;
      }

      if (!cardData.numero.trim()) {
        toast.error('El número de tarjeta es obligatorio');
        setLoading(false);
        return;
      }

      // Validar tarjeta y PIN con el backend
      const response = await tarjetaService.validarTarjeta({
        tar_numero_tarjeta: cardData.numero,
        tar_pin: cardData.pin
      });

      if (response.data.valida) {
        setCurrentScreen('menu');
        toast.success(`Bienvenido ${response.data.usuario.usuario}. PIN correcto.`);
      } else {
        toast.error(response.data.mensaje || 'Número de tarjeta o PIN incorrecto');
      }
    } catch (error) {
      console.error('Error al validar tarjeta:', error);
      toast.error(error.response?.data?.detail || 'Error al validar la tarjeta');
    } finally {
      setLoading(false);
    }
  };

  const handleRetiroMonto = (monto) => {
    if (monto % 10 !== 0) {
      toast.error('Solo se permiten montos múltiplos de $10');
      return;
    }
    setRetiroData({ ...retiroData, monto });
    setCurrentScreen('confirmRetiro');
  };

  const handleConfirmRetiro = async (imprimirBoucher) => {
    setRetiroData({ ...retiroData, imprimirBoucher });
    setCurrentScreen('processing');
    setProcessingStep('validando');
    setProcessingMessage('Validando datos de la transacción...');
    setLoading(true);
    
    try {
      // Primero necesitamos obtener la información de la cuenta asociada a la tarjeta
      const validacionResponse = await tarjetaService.validarTarjeta({
        tar_numero_tarjeta: cardData.numero,
        tar_pin: cardData.pin
      });

      if (!validacionResponse.data.valida) {
        throw new Error('Tarjeta no válida');
      }

      // Procesar retiro con tarjeta
      const retiroRequest = {
        tipo_retiro: 'CON_TARJETA',
        ret_monto: retiroData.monto,
        cuen_id: validacionResponse.data.usuario.cuenta_id,
        tar_numero_tarjeta: cardData.numero,
        imprimir_boucher: imprimirBoucher ? "SI" : "NO",
        caj_id: cajeroSeleccionado
      };

      console.log('=== DEBUGGING RETIRO CON TARJETA ===');
      console.log('retiroRequest:', retiroRequest);
      console.log('cajeroSeleccionado:', cajeroSeleccionado);
      console.log('validacionResponse.data:', validacionResponse.data);
      console.log('retiroData:', retiroData);
      console.log('cardData:', cardData);
      console.log('imprimirBoucher:', imprimirBoucher);
      console.log('=== FIN DEBUGGING ===');

      await transaccionService.procesarRetiro(retiroRequest);

      // Simular proceso de retiro
      setTimeout(() => {
        setProcessingStep('tarjeta');
        setProcessingMessage('Retire su tarjeta del cajero');
        
        setTimeout(() => {
          setProcessingStep('dinero');
          setProcessingMessage('Retire su dinero del cajero');
          
          setTimeout(() => {
            if (imprimirBoucher) {
              setProcessingStep('boucher');
              setProcessingMessage('Generando boucher... Por favor espere');
              
              setTimeout(() => {
                setProcessingMessage('Retire su boucher del cajero');
                
                setTimeout(() => {
                  setProcessingStep('success');
                  setProcessingMessage('Transacción exitosa. Gracias por usar nuestros servicios.');
                  setTimeout(() => {
                    resetCajero();
                  }, 3000);
                }, 3000);
              }, 3000);
            } else {
              setProcessingStep('success');
              setProcessingMessage('Transacción exitosa. Gracias por usar nuestros servicios.');
              setTimeout(() => {
                resetCajero();
              }, 3000);
            }
          }, 3000);
        }, 3000);
      }, 2000);

    } catch (error) {
      console.error('Error en retiro con tarjeta:', error);
      console.log('=== ERROR DEBUGGING ===');
      console.log('Error status:', error.response?.status);
      console.log('Error data:', error.response?.data);
      console.log('Error config:', error.config);
      console.log('Error request data:', error.config?.data);
      console.log('=== FIN ERROR DEBUGGING ===');
      
      let errorMessage = 'Error al procesar el retiro';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      toast.error(errorMessage);
      resetCajero();
    } finally {
      setLoading(false);
    }
  };

  const handleRetiroSinTarjetaSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Validar que todos los campos estén llenos
      if (!retiroSinTarjeta.numero_celular || !retiroSinTarjeta.monto || !retiroSinTarjeta.codigo) {
        toast.error('Todos los campos son obligatorios');
        setLoading(false);
        return;
      }

      // Validar código
      const response = await retiroSinTarjetaService.validarCodigo({
        codigo: retiroSinTarjeta.codigo,
        telefono: retiroSinTarjeta.numero_celular
      });

      if (response.data.valido) {
        // Verificar que el monto coincida
        if (parseFloat(retiroSinTarjeta.monto) !== response.data.monto) {
          toast.error(`El monto ingresado no coincide. El monto registrado es $${response.data.monto}`);
          setLoading(false);
          return;
        }

        // Procesar el retiro exitosamente
        const retiroResponse = await retiroSinTarjetaService.procesarRetiro(response.data.codigo_id);
        
        let mensaje = 'Código validado correctamente. Procesando retiro...';
        if (retiroResponse.data.tipo_tarjeta === 'CREDITO') {
          mensaje += ' (Procesado como tarjeta de crédito - sin descuento de cuenta)';
        } else if (retiroResponse.data.tipo_tarjeta === 'DEBITO') {
          mensaje += ` (Nuevo saldo: $${retiroResponse.data.nuevo_saldo})`;
        }
        
        toast.success(mensaje);
        setCurrentScreen('processing');
        setProcessingStep('dinero');
        setProcessingMessage('Retire su dinero del cajero');
        
        setTimeout(() => {
          setProcessingStep('success');
          setProcessingMessage('Retiro sin tarjeta exitoso. Gracias por usar nuestros servicios.');
          setTimeout(() => {
            resetCajero();
          }, 3000);
        }, 5000);
        
      } else {
        // Error en validación - usar el mensaje del backend
        const errorMessage = response.data.mensaje || 'Código inválido o expirado';
        
        // Incrementar contador de intentos en caso de error de validación
        const nuevosIntentos = retiroSinTarjeta.intentos + 1;
        
        if (nuevosIntentos >= 3) {
          // Solo intentar marcar como NO USADO si el código existe en la base
          if (response.data.codigo_existe) {
            try {
              const marcarResponse = await retiroSinTarjetaService.marcarCodigoNoUsado({
                codigo: retiroSinTarjeta.codigo,
                telefono: retiroSinTarjeta.numero_celular
              });
              
              if (marcarResponse.data.codigo_encontrado) {
                toast.error(`Código bloqueado por 3 intentos fallidos. ${errorMessage}`);
              } else {
                toast.error(`3 intentos fallidos completados. ${errorMessage}`);
              }
            } catch (marcarError) {
              console.error('Error al marcar código como no usado:', marcarError);
              toast.error(`3 intentos fallidos. ${errorMessage}`);
            }
          } else {
            toast.error(`3 intentos fallidos completados. ${errorMessage}`);
          }
          
          // Reiniciar cajero después de 3 intentos
          setTimeout(() => {
            resetCajero();
          }, 3000);
        } else {
          // Mostrar error y permitir reintento
          setRetiroSinTarjeta({
            ...retiroSinTarjeta,
            intentos: nuevosIntentos
          });
          toast.error(`${errorMessage}. Intento ${nuevosIntentos}/3`);
        }
      }
    } catch (error) {
      console.error('Error en retiro sin tarjeta:', error);
      let errorMessage = 'Error al procesar el retiro sin tarjeta';
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.mensaje) {
        errorMessage = error.response.data.mensaje;
      }

      // Incrementar contador de intentos en caso de error de conexión
      const nuevosIntentos = retiroSinTarjeta.intentos + 1;
      
      if (nuevosIntentos >= 3) {
        toast.error(`3 intentos fallidos por error de conexión. ${errorMessage}`);
        
        // Reiniciar cajero después de 3 intentos
        setTimeout(() => {
          resetCajero();
        }, 3000);
      } else {
        // Mostrar error y permitir reintento
        setRetiroSinTarjeta({
          ...retiroSinTarjeta,
          intentos: nuevosIntentos
        });
        toast.error(`${errorMessage}. Intento ${nuevosIntentos}/3`);
      }
    }
    
    setLoading(false);
  };

  const resetCajero = () => {
    setCurrentScreen('main');
    setCardData({ numero: '', pin: '' });
    setRetiroData({ monto: 0, imprimirBoucher: false });
    setRetiroSinTarjeta({ numero_celular: '', monto: '', codigo: '', intentos: 0 });
    setProcessingStep('');
    setProcessingMessage('');
    setLoading(false);
    setCajeroSeleccionado(null);
  };

  const renderMainScreen = () => (
    <div className="text-center">
      <div className="mb-5">
        <img 
          src="https://cdn.worldvectorlogo.com/logos/banco-pichincha.svg" 
          alt="Banco Pichincha" 
          style={{ height: '80px', marginBottom: '20px' }}
        />
        <h2 className="text-primary">Cajero Automático</h2>
        <h3 className="text-secondary">Banco Pichincha</h3>
      </div>
      
      <div className="mb-4">
        <Alert variant="info" className="text-center">
          <i className="bi bi-info-circle me-2"></i>
          <strong>Instrucciones:</strong>
          <br />
          • Presione la tecla <kbd>T</kbd> para insertar su tarjeta
          <br />
          • Use el botón "Retiro sin Tarjeta" para retiros con código
        </Alert>
      </div>

      <Row className="justify-content-center">
        <Col md={8}>
          <Card className="border-2 border-primary">
            <Card.Body className="p-4">
              <div className="mb-4">
                <i className="bi bi-credit-card text-primary" style={{ fontSize: '4rem' }}></i>
                <h4 className="mt-3">Inserte su tarjeta</h4>
                <p className="text-muted">Presione la tecla 'T' para simular la inserción de tarjeta</p>
              </div>
              
              <hr />
              
              <Button 
                variant="outline-success" 
                size="lg" 
                className="w-100 mt-3"
                onClick={() => setCurrentScreen('retiroSinTarjeta')}
              >
                <i className="bi bi-phone me-2"></i>
                Retiro sin Tarjeta
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );

  const renderCajeroSelection = () => (
    <div className="text-center">
      <h3 className="text-primary mb-4">
        <i className="bi bi-credit-card-fill me-2"></i>
        Tarjeta Detectada
      </h3>
      
      <Alert variant="success" className="mb-4">
        <i className="bi bi-check-circle me-2"></i>
        Tarjeta insertada correctamente. Seleccione el cajero para continuar.
      </Alert>
      
      <h4 className="mb-4">Seleccione el Cajero</h4>
      
      <Row className="justify-content-center">
        <Col md={8}>
          {cajerosLoading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-primary mb-3" role="status">
                <span className="visually-hidden">Cargando cajeros...</span>
              </div>
              <p className="text-muted">Cargando cajeros disponibles...</p>
            </div>
          ) : cajeros.length > 0 ? (
            <Row className="g-3">
              {cajeros.map((cajero) => (
                <Col md={6} key={cajero.caj_id}>
                  <Card 
                    className="h-100 shadow-sm cajero-card" 
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleCajeroSelection(cajero.caj_id)}
                  >
                    <Card.Body className="text-center p-4">
                      <i className="bi bi-geo-alt-fill text-primary mb-3" style={{ fontSize: '2rem' }}></i>
                      <h5 className="card-title">{cajero.caj_ubicacion}</h5>
                      <p className="card-text text-muted">
                        <small>
                          <i className="bi bi-building me-1"></i>
                          {cajero.caj_sucursal}
                        </small>
                        <br />
                        <small>
                          <i className="bi bi-gear me-1"></i>
                          {cajero.caj_tipo}
                        </small>
                      </p>
                      <Alert variant="success" className="mb-0 py-1">
                        <i className="bi bi-check-circle me-1"></i>
                        <small>{cajero.caj_estado}</small>
                      </Alert>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          ) : (
            <Alert variant="warning">
              <i className="bi bi-exclamation-triangle me-2"></i>
              No hay cajeros disponibles en este momento.
            </Alert>
          )}
          
          <div className="mt-4">
            <Button variant="outline-secondary" onClick={resetCajero}>
              <i className="bi bi-arrow-left me-2"></i>
              Cancelar y Expulsar Tarjeta
            </Button>
          </div>
        </Col>
      </Row>
    </div>
  );

  const renderCardInserted = () => (
    <div className="text-center">
      <h3 className="text-success mb-4">
        <i className="bi bi-credit-card-fill me-2"></i>
        Tarjeta Insertada
      </h3>
      
      <Form onSubmit={handlePinSubmit}>
        <Row className="justify-content-center">
          <Col md={6}>
            <Card>
              <Card.Body className="p-4">
                <Form.Group className="mb-3">
                  <Form.Label><strong>Número de Tarjeta</strong></Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="1234-5678-9012-3456"
                    value={cardData.numero}
                    onChange={(e) => setCardData({...cardData, numero: e.target.value})}
                    required
                  />
                </Form.Group>
                
                <Form.Group className="mb-4">
                  <Form.Label><strong>PIN de 4 dígitos</strong></Form.Label>
                  <Form.Control
                    type="password"
                    placeholder="••••"
                    maxLength="4"
                    value={cardData.pin}
                    onChange={(e) => setCardData({...cardData, pin: e.target.value})}
                    required
                  />
                </Form.Group>
                
                <div className="d-grid gap-2">
                  <Button 
                    variant="primary" 
                    type="submit" 
                    size="lg"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Validando...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-circle me-2"></i>
                        Confirmar PIN
                      </>
                    )}
                  </Button>
                  <Button variant="outline-secondary" onClick={resetCajero}>
                    <i className="bi bi-arrow-left me-2"></i>
                    Cancelar
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Form>
    </div>
  );

  const renderMenu = () => (
    <div className="text-center">
      <h3 className="text-primary mb-2">Menú Principal</h3>
      {cajeroSeleccionado && cajeros.length > 0 && (
        <div className="mb-4">
          <Alert variant="light" className="mx-auto border-primary" style={{ maxWidth: '500px' }}>
            <Row className="align-items-center">
              <Col xs={8}>
                <small className="text-muted">
                  <i className="bi bi-geo-alt me-1"></i>
                  <strong>Ubicación:</strong> {cajeros.find(c => c.caj_id === cajeroSeleccionado)?.caj_ubicacion}
                </small>
              </Col>
              <Col xs={4} className="text-end">
                <small className="text-success">
                  <i className="bi bi-check-circle-fill me-1"></i>
                  ACTIVO
                </small>
              </Col>
            </Row>
          </Alert>
        </div>
      )}
      
      <Row className="justify-content-center">
        <Col md={8}>
          <Row className="g-3">
            <Col md={6}>
              <Button 
                variant="primary" 
                size="lg" 
                className="w-100 h-100 p-4"
                onClick={() => setCurrentScreen('retiro')}
              >
                <i className="bi bi-cash-stack d-block mb-2" style={{ fontSize: '2rem' }}></i>
                <strong>Retiro</strong>
              </Button>
            </Col>
            <Col md={6}>
              <Button 
                variant="outline-primary" 
                size="lg" 
                className="w-100 h-100 p-4"
                disabled
              >
                <i className="bi bi-receipt d-block mb-2" style={{ fontSize: '2rem' }}></i>
                <strong>Consulta Saldo</strong>
                <br />
                <small>(No disponible)</small>
              </Button>
            </Col>
            <Col md={6}>
              <Button 
                variant="outline-secondary" 
                size="lg" 
                className="w-100 h-100 p-4"
                onClick={resetCajero}
              >
                <i className="bi bi-box-arrow-right d-block mb-2" style={{ fontSize: '2rem' }}></i>
                <strong>Salir</strong>
              </Button>
            </Col>
          </Row>
        </Col>
      </Row>
    </div>
  );

  const renderRetiro = () => (
    <div className="text-center">
      <h3 className="text-primary mb-4">Seleccione el Monto a Retirar</h3>
      
      <Row className="justify-content-center">
        <Col md={8}>
          <Row className="g-3 mb-4">
            {[10, 20, 40, 60].map(monto => (
              <Col md={6} key={monto}>
                <Button 
                  variant="outline-primary" 
                  size="lg" 
                  className="w-100 p-3"
                  onClick={() => handleRetiroMonto(monto)}
                >
                  <i className="bi bi-cash me-2"></i>
                  ${monto}.00
                </Button>
              </Col>
            ))}
          </Row>
          
          <Card className="mb-3">
            <Card.Body>
              <h5>Otro Monto</h5>
              <Form.Group className="mb-3">
                <Form.Control
                  type="number"
                  placeholder="Ingrese monto (múltiplos de $10)"
                  min="10"
                  step="10"
                  onChange={(e) => setRetiroData({...retiroData, monto: parseInt(e.target.value) || 0})}
                />
              </Form.Group>
              <Button 
                variant="primary" 
                onClick={() => handleRetiroMonto(retiroData.monto)}
                disabled={retiroData.monto < 10 || retiroData.monto % 10 !== 0}
              >
                Confirmar Monto
              </Button>
            </Card.Body>
          </Card>
          
          <Button variant="outline-secondary" onClick={() => setCurrentScreen('menu')}>
            <i className="bi bi-arrow-left me-2"></i>
            Volver al Menú
          </Button>
        </Col>
      </Row>
    </div>
  );

  const renderConfirmRetiro = () => (
    <div className="text-center">
      <h3 className="text-primary mb-4">Confirmar Retiro</h3>
      
      <Row className="justify-content-center">
        <Col md={6}>
          <Card className="mb-4">
            <Card.Body>
              <h4 className="text-success">${retiroData.monto}.00</h4>
              <p className="text-muted">Monto a retirar</p>
              
              {cajeroSeleccionado && cajeros.length > 0 && (
                <div className="mb-3">
                  <Alert variant="light" className="border-info">
                    <small>
                      <i className="bi bi-geo-alt me-1"></i>
                      <strong>Cajero:</strong> {cajeros.find(c => c.caj_id === cajeroSeleccionado)?.caj_ubicacion}
                      <br />
                      <i className="bi bi-building me-1"></i>
                      <strong>Sucursal:</strong> {cajeros.find(c => c.caj_id === cajeroSeleccionado)?.caj_sucursal}
                    </small>
                  </Alert>
                </div>
              )}
              
              <Alert variant="warning">
                <i className="bi bi-printer me-2"></i>
                <strong>¿Desea imprimir boucher?</strong>
                <br />
                <small>Costo adicional: $0.36</small>
              </Alert>
              
              <div className="d-grid gap-2">
                <Button 
                  variant="success" 
                  size="lg"
                  onClick={() => handleConfirmRetiro(true)}
                >
                  <i className="bi bi-printer me-2"></i>
                  Sí, imprimir boucher (+$0.36)
                </Button>
                <Button 
                  variant="primary" 
                  size="lg"
                  onClick={() => handleConfirmRetiro(false)}
                >
                  <i className="bi bi-x-circle me-2"></i>
                  No, sin boucher
                </Button>
                <Button 
                  variant="outline-secondary"
                  onClick={() => setCurrentScreen('retiro')}
                >
                  <i className="bi bi-arrow-left me-2"></i>
                  Cancelar
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );

  const renderRetiroSinTarjeta = () => (
    <div className="text-center">
      <h3 className="text-success mb-4">
        <i className="bi bi-phone me-2"></i>
        Retiro sin Tarjeta
      </h3>
      
      <Row className="justify-content-center">
        <Col md={6}>
          <Card>
            <Card.Body className="p-4">
              <Form onSubmit={handleRetiroSinTarjetaSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label><strong>Número de Celular</strong></Form.Label>
                  <Form.Control
                    type="tel"
                    placeholder="0987654321"
                    value={retiroSinTarjeta.numero_celular}
                    onChange={(e) => setRetiroSinTarjeta({
                      ...retiroSinTarjeta, 
                      numero_celular: e.target.value
                    })}
                    required
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label><strong>Monto a Retirar</strong></Form.Label>
                  <Form.Control
                    type="number"
                    placeholder="Ejemplo: 50"
                    value={retiroSinTarjeta.monto}
                    onChange={(e) => setRetiroSinTarjeta({
                      ...retiroSinTarjeta, 
                      monto: e.target.value
                    })}
                    required
                  />
                  <Form.Text className="text-muted">
                    Debe coincidir con el monto registrado
                  </Form.Text>
                </Form.Group>
                
                <Form.Group className="mb-4">
                  <Form.Label><strong>Código de 6 dígitos</strong></Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="123456"
                    maxLength="6"
                    value={retiroSinTarjeta.codigo}
                    onChange={(e) => setRetiroSinTarjeta({
                      ...retiroSinTarjeta, 
                      codigo: e.target.value
                    })}
                    required
                  />
                  <Form.Text className="text-muted">
                    Código generado desde el dashboard
                  </Form.Text>
                </Form.Group>

                {retiroSinTarjeta.intentos > 0 && (
                  <Alert variant="warning" className="mb-3">
                    <i className="fas fa-exclamation-triangle"></i>
                    {' '}Intento {retiroSinTarjeta.intentos}/3. 
                    {retiroSinTarjeta.intentos === 2 && ' ¡Último intento!'}
                  </Alert>
                )}
                
                <div className="d-grid gap-2">
                  <Button 
                    variant="success" 
                    type="submit" 
                    size="lg"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Validando...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-circle me-2"></i>
                        Procesar Retiro
                      </>
                    )}
                  </Button>
                  <Button 
                    variant="outline-secondary" 
                    onClick={resetCajero}
                  >
                    <i className="bi bi-arrow-left me-2"></i>
                    Volver al Inicio
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );

  const renderProcessing = () => (
    <div className="text-center">
      <h3 className="text-warning mb-4">
        <i className="bi bi-hourglass-split me-2"></i>
        Procesando Transacción
      </h3>
      
      <Row className="justify-content-center">
        <Col md={6}>
          <Card className="border-warning">
            <Card.Body className="p-5">
              <div className="mb-4">
                {processingStep === 'validando' && (
                  <i className="bi bi-shield-check text-primary" style={{ fontSize: '4rem' }}></i>
                )}
                {processingStep === 'tarjeta' && (
                  <i className="bi bi-credit-card text-warning" style={{ fontSize: '4rem' }}></i>
                )}
                {processingStep === 'dinero' && (
                  <i className="bi bi-cash-stack text-success" style={{ fontSize: '4rem' }}></i>
                )}
                {processingStep === 'boucher' && (
                  <i className="bi bi-printer text-info" style={{ fontSize: '4rem' }}></i>
                )}
                {processingStep === 'success' && (
                  <i className="bi bi-check-circle text-success" style={{ fontSize: '4rem' }}></i>
                )}
              </div>
              
              <h4 className="mb-3">{processingMessage}</h4>
              
              {processingStep !== 'success' && (
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Cargando...</span>
                </div>
              )}
              
              {processingStep === 'success' && (
                <Alert variant="success" className="mt-3">
                  <i className="bi bi-check-circle me-2"></i>
                  ¡Operación completada exitosamente!
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );

  return (
    <Container className="py-5">
      <div style={{ 
        minHeight: '80vh', 
        backgroundColor: '#f8f9fa', 
        padding: '30px',
        borderRadius: '15px',
        border: '3px solid #0d6efd'
      }}>
        {currentScreen === 'main' && renderMainScreen()}
        {currentScreen === 'cajeroSelection' && renderCajeroSelection()}
        {currentScreen === 'cardInserted' && renderCardInserted()}
        {currentScreen === 'menu' && renderMenu()}
        {currentScreen === 'retiro' && renderRetiro()}
        {currentScreen === 'confirmRetiro' && renderConfirmRetiro()}
        {currentScreen === 'retiroSinTarjeta' && renderRetiroSinTarjeta()}
        {currentScreen === 'processing' && renderProcessing()}
      </div>
    </Container>
  );
}

export default Cajero;
