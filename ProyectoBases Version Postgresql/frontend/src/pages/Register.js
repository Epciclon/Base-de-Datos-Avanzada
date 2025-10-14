import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, ProgressBar } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { clienteService, cuentaService } from '../services/api';
import { useNavigate } from 'react-router-dom';

function Register() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [tipoCuenta, setTipoCuenta] = useState('');
  
  // Datos del cliente (cambia según el tipo)
  const [clienteData, setClienteData] = useState({
    per_nombres: '', // Para empresas será "Razón Social"
    per_apellidos: '', // Para empresas será "Nombre Comercial"
    per_fecha_nacimiento: '',
    per_genero: '',
    per_telefono: '',
    per_correo: '',
    per_direccion: '',
    per_tipo: '', // Se establecerá según el tipo de cuenta
    // Campos específicos para Persona Natural
    identificacion: '', // Cédula
    estado_civil: '',
    profesion: '',
    // Campos específicos para Persona Jurídica
    ruc: '', // RUC de la empresa
    representante_legal: '',
    tipo_entidad: '',
    fecha_constitucion: '',
    actividad_economica: ''
  });

  // Datos de la cuenta
  const [cuentaData, setCuentaData] = useState({
    cuen_usuario: '',
    cuen_password: '',
    cuen_saldo: '0.00' // Permitir saldo inicial de $0 para cuentas de ahorro
  });

  const handleClienteChange = (e) => {
    setClienteData({
      ...clienteData,
      [e.target.name]: e.target.value
    });
  };

  const handleCuentaChange = (e) => {
    setCuentaData({
      ...cuentaData,
      [e.target.name]: e.target.value
    });
  };

  const handleTipoCuentaSelect = (tipo) => {
    setTipoCuenta(tipo);
    // Establecer el tipo de persona según la cuenta
    setClienteData(prev => ({
      ...prev,
      per_tipo: tipo === 'AHORRO' ? 'NATURAL' : 'JURIDICA',
      // Limpiar campos que no aplican según el tipo
      ...(tipo === 'AHORRO' ? {
        ruc: '',
        representante_legal: '',
        tipo_entidad: '',
        fecha_constitucion: '',
        actividad_economica: ''
      } : {
        identificacion: '',
        estado_civil: '',
        profesion: ''
      })
    }));
    setCurrentStep(2);
  };

  const handleBackToStep1 = () => {
    setCurrentStep(1);
    setTipoCuenta('');
    // Limpiar datos del cliente
    setClienteData({
      PER_NOMBRES: '',
      PER_APELLIDOS: '',
      per_fecha_nacimiento: '',
      per_genero: '',
      per_telefono: '',
      per_correo: '',
      per_direccion: '',
      per_tipo: '',
      identificacion: '',
      estado_civil: '',
      profesion: '',
      ruc: '',
      representante_legal: '',
      tipo_entidad: '',
      fecha_constitucion: '',
      actividad_economica: ''
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Validaciones básicas del frontend
      if (!clienteData.per_nombres.trim()) {
        const nombreLabel = tipoCuenta === 'AHORRO' ? 'Nombres' : 'Razón Social';
        toast.error(`El campo ${nombreLabel} es obligatorio`);
        setLoading(false);
        return;
      }
      
      if (!clienteData.per_apellidos.trim()) {
        const apellidoLabel = tipoCuenta === 'AHORRO' ? 'Apellidos' : 'Nombre Comercial';
        toast.error(`El campo ${apellidoLabel} es obligatorio`);
        setLoading(false);
        return;
      }
      
      if (!clienteData.per_correo.trim()) {
        toast.error('El campo Correo electrónico es obligatorio');
        setLoading(false);
        return;
      }
      
      // Validaciones específicas por tipo de cuenta
      if (tipoCuenta === 'AHORRO') {
        // Validaciones para Persona Natural
        if (!clienteData.identificacion.trim()) {
          toast.error('El campo Cédula es obligatorio');
          setLoading(false);
          return;
        }
        
        if (!clienteData.per_fecha_nacimiento) {
          toast.error('El campo Fecha de Nacimiento es obligatorio');
          setLoading(false);
          return;
        }
        
        if (!clienteData.per_genero) {
          toast.error('El campo Género es obligatorio');
          setLoading(false);
          return;
        }

        if (!clienteData.estado_civil) {
          toast.error('El campo Estado Civil es obligatorio');
          setLoading(false);
          return;
        }

        if (!clienteData.profesion.trim()) {
          toast.error('El campo Profesión es obligatorio');
          setLoading(false);
          return;
        }
      } else {
        // Validaciones para Persona Jurídica
        if (!clienteData.ruc.trim()) {
          toast.error('El campo RUC es obligatorio');
          setLoading(false);
          return;
        }

        if (!clienteData.representante_legal.trim()) {
          toast.error('El campo Representante Legal es obligatorio');
          setLoading(false);
          return;
        }

        if (!clienteData.tipo_entidad) {
          toast.error('El campo Tipo de Entidad es obligatorio');
          setLoading(false);
          return;
        }

        if (!clienteData.fecha_constitucion) {
          toast.error('El campo Fecha de Constitución es obligatorio');
          setLoading(false);
          return;
        }

        if (!clienteData.actividad_economica.trim()) {
          toast.error('El campo Actividad Económica es obligatorio');
          setLoading(false);
          return;
        }
      }

      if (!cuentaData.cuen_usuario.trim()) {
        toast.error('El campo Usuario de la cuenta es obligatorio');
        setLoading(false);
        return;
      }

      if (!cuentaData.cuen_password.trim()) {
        toast.error('El campo Contraseña es obligatorio');
        setLoading(false);
        return;
      }

      if (cuentaData.cuen_password.length < 6) {
        toast.error('La contraseña debe tener al menos 6 caracteres');
        setLoading(false);
        return;
      }

      // Paso 1: Registrar el cliente
      console.log('Registrando cliente...');
      
      // Preparar datos base del cliente
      const clienteBase = {
        per_nombres: clienteData.per_nombres,
        per_apellidos: clienteData.per_apellidos,
        per_fecha_nacimiento: clienteData.per_fecha_nacimiento ? 
          new Date(clienteData.per_fecha_nacimiento).toISOString() : 
          clienteData.per_fecha_nacimiento,
        per_genero: clienteData.per_genero,
        per_telefono: clienteData.per_telefono,
        per_correo: clienteData.per_correo,
        per_direccion: clienteData.per_direccion,
        per_tipo: clienteData.per_tipo,
        cli_estado: 'ACTIVO'
      };

      // Agregar campos específicos según el tipo de cuenta
      let clienteToSend;
      if (tipoCuenta === 'AHORRO') {
        // Para personas naturales (cuenta de ahorros)
        clienteToSend = {
          ...clienteBase,
          identificacion: clienteData.identificacion,
          estado_civil: clienteData.estado_civil,
          profesion: clienteData.profesion
        };
      } else {
        // Para personas jurídicas (cuenta corriente)
        clienteToSend = {
          ...clienteBase,
          ruc: clienteData.ruc,
          representante_legal: clienteData.representante_legal,
          tipo_entidad: clienteData.tipo_entidad,
          fecha_constitucion: clienteData.fecha_constitucion ? 
            new Date(clienteData.fecha_constitucion).toISOString() : 
            clienteData.fecha_constitucion,
          actividad_economica: clienteData.actividad_economica
        };
      }

      console.log('Datos del cliente:', JSON.stringify(clienteToSend, null, 2));

      const clienteResponse = await clienteService.crear(clienteToSend);
      console.log('Cliente creado:', clienteResponse.data);

      // Paso 2: Crear la cuenta bancaria
      console.log('Creando cuenta bancaria...');
      
      const cuentaToSend = {
        ...cuentaData,
        cuen_tipo: tipoCuenta,
        cuen_estado: 'ACTIVA',
        per_id: clienteResponse.data.per_id,
        cli_id: clienteResponse.data.cli_id
      };

      console.log('Datos de la cuenta:', JSON.stringify(cuentaToSend, null, 2));

      const cuentaResponse = await cuentaService.crear(cuentaToSend);
      console.log('Cuenta creada:', cuentaResponse.data);
      
      toast.success('¡Registro exitoso! Cliente y cuenta bancaria creados correctamente. Ya puedes iniciar sesión.', {
        position: "top-right",
        autoClose: 6000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      
      setTimeout(() => {
        navigate('/login');
      }, 3000);
      
    } catch (error) {
      console.error('Error completo:', error);
      
      let errorMessage = 'Error inesperado durante el registro';
      
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;
        
        switch (status) {
          case 422:
            if (data.detail && Array.isArray(data.detail)) {
              // Errores de validación específicos
              const validationErrors = data.detail.map(err => {
                const field = err.loc?.[err.loc.length - 1] || 'campo';
                const fieldNames = {
                  'per_nombres': 'Nombres',
                  'per_apellidos': 'Apellidos', 
                  'per_correo': 'Correo electrónico',
                  'per_telefono': 'Teléfono',
                  'per_fecha_nacimiento': 'Fecha de nacimiento',
                  'identificacion': 'Número de identificación',
                  'estado_civil': 'Estado civil',
                  'profesion': 'Profesión',
                  'cuen_usuario': 'Usuario de la cuenta',
                  'cuen_password': 'Contraseña',
                  'cuen_saldo': 'Saldo inicial'
                };
                const friendlyField = fieldNames[field] || field;
                return `${friendlyField}: ${err.msg || 'Valor inválido'}`;
              }).join('. ');
              errorMessage = `Errores de validación: ${validationErrors}`;
            } else if (typeof data.detail === 'string') {
              errorMessage = data.detail;
            } else {
              errorMessage = 'Datos enviados no son válidos. Verifica que todos los campos estén correctos.';
            }
            break;
            
          case 400:
            errorMessage = data.detail || 'Solicitud incorrecta. Verifica los datos ingresados.';
            break;
            
          case 409:
            errorMessage = 'Ya existe un cliente registrado con esta identificación, correo electrónico o usuario de cuenta.';
            break;
            
          case 500:
            errorMessage = 'Error interno del servidor. Por favor, intenta nuevamente más tarde.';
            break;
            
          default:
            errorMessage = data.detail || `Error del servidor (${status}). Contacta al soporte técnico.`;
        }
      } else if (error.request) {
        errorMessage = 'No se pudo conectar con el servidor. Verifica tu conexión a internet.';
      } else {
        errorMessage = 'Error de configuración. Contacta al soporte técnico.';
      }
      
      toast.error(errorMessage, {
        position: "top-right",
        autoClose: 8000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      
    } finally {
      setLoading(false);
    }
  };

  // Componente para el Paso 1: Selección de tipo de cuenta
  const renderStep1 = () => (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col lg={8}>
          <Card className="shadow">
            <Card.Header className="bg-primary text-white text-center">
              <h3 className="mb-0">
                <i className="bi bi-bank2 me-2"></i>
                Bienvenido al Banco Pichincha
              </h3>
            </Card.Header>
            <Card.Body className="p-5">
              <div className="text-center mb-4">
                <h4 className="text-pichincha-blue">¿Qué tipo de cuenta deseas crear?</h4>
                <p className="text-muted">
                  Selecciona el tipo de cuenta según tu perfil
                </p>
              </div>

              <Row className="g-4">
                <Col md={6}>
                  <Card 
                    className="h-100 border-2 border-primary card-hover cursor-pointer"
                    onClick={() => handleTipoCuentaSelect('AHORRO')}
                    style={{ cursor: 'pointer' }}
                  >
                    <Card.Body className="text-center p-4">
                      <div className="mb-3">
                        <i className="bi bi-person-fill text-primary" style={{fontSize: '4rem'}}></i>
                      </div>
                      <Card.Title className="h4 text-primary">Cuenta de Ahorros</Card.Title>
                      <Card.Text className="text-muted">
                        <strong>Para Personas Naturales</strong>
                        <br />
                        • Registro con cédula de identidad
                        <br />
                        • Tarjetas de débito disponibles
                        <br />
                        • Ideal para ahorros personales
                        <br />
                        • Gestión de finanzas familiares
                      </Card.Text>
                      <Button variant="primary" size="lg" className="w-100">
                        Registrar Persona Natural
                      </Button>
                    </Card.Body>
                  </Card>
                </Col>

                <Col md={6}>
                  <Card 
                    className="h-100 border-2 border-success card-hover cursor-pointer"
                    onClick={() => handleTipoCuentaSelect('CORRIENTE')}
                    style={{ cursor: 'pointer' }}
                  >
                    <Card.Body className="text-center p-4">
                      <div className="mb-3">
                        <i className="bi bi-building text-success" style={{fontSize: '4rem'}}></i>
                      </div>
                      <Card.Title className="h4 text-success">Cuenta Corriente</Card.Title>
                      <Card.Text className="text-muted">
                        <strong>Para Personas Jurídicas</strong>
                        <br />
                        • Registro con RUC empresarial
                        <br />
                        • Tarjetas débito y crédito
                        <br />
                        • Ideal para empresas y negocios
                        <br />
                        • Transacciones comerciales
                      </Card.Text>
                      <Button variant="success" size="lg" className="w-100">
                        Registrar Empresa
                      </Button>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              <div className="text-center mt-4">
                <small className="text-muted">
                  Al continuar, procederás a completar el formulario de registro
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );

  // Componente para el Paso 2: Formulario completo
  const renderStep2 = () => (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col lg={10}>
          <Card className="shadow">
            <Card.Header className="bg-primary text-white">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h3 className="mb-0">
                    <i className="bi bi-person-plus-fill me-2"></i>
                    {tipoCuenta === 'AHORRO' ? 'Registro Persona Natural' : 'Registro Persona Jurídica'}
                  </h3>
                  <small>Cuenta {tipoCuenta === 'AHORRO' ? 'de Ahorros' : 'Corriente'}</small>
                </div>
                <Button variant="outline-light" size="sm" onClick={handleBackToStep1}>
                  <i className="bi bi-arrow-left me-1"></i>
                  Cambiar tipo de cuenta
                </Button>
              </div>
            </Card.Header>
            <Card.Body className="p-4">
              {/* Barra de progreso */}
              <div className="mb-4">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <small className="text-muted">Paso 2 de 2</small>
                  <small className="text-muted">75%</small>
                </div>
                <ProgressBar now={75} />
              </div>

              <Form onSubmit={handleSubmit}>
                {/* Información Personal */}
                <Card className="mb-4">
                  <Card.Header className="bg-light">
                    <h5 className="mb-0">
                      <i className="bi bi-person-circle me-2"></i>
                      {tipoCuenta === 'AHORRO' ? 'Información Personal' : 'Información de la Empresa'}
                    </h5>
                  </Card.Header>
                  <Card.Body>
                    <Row className="g-3">
                      {/* Campos para Persona Natural (Cuenta de Ahorros) */}
                      {tipoCuenta === 'AHORRO' && (
                        <>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-person-fill me-2"></i>
                                Nombres *
                              </Form.Label>
                              <Form.Control
                                type="text"
                                name="per_nombres"
                                value={clienteData.per_nombres}
                                onChange={handleClienteChange}
                                placeholder="Ingresa tus nombres"
                                required
                              />
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-person-fill me-2"></i>
                                Apellidos *
                              </Form.Label>
                              <Form.Control
                                type="text"
                                name="per_apellidos"
                                value={clienteData.per_apellidos}
                                onChange={handleClienteChange}
                                placeholder="Ingresa tus apellidos"
                                required
                              />
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-card-text me-2"></i>
                                Cédula de Identidad *
                              </Form.Label>
                              <Form.Control
                                type="text"
                                name="identificacion"
                                value={clienteData.identificacion}
                                onChange={handleClienteChange}
                                placeholder="0123456789"
                                minLength="10"
                                maxLength="10"
                                pattern="[0-9]{10}"
                                required
                              />
                              <Form.Text className="text-muted">
                                Ingresa tu número de cédula sin guiones
                              </Form.Text>
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>Estado Civil *</Form.Label>
                              <Form.Select
                                name="estado_civil"
                                value={clienteData.estado_civil}
                                onChange={handleClienteChange}
                                required
                              >
                                <option value="">Selecciona tu estado civil</option>
                                <option value="SOLTERO">Soltero/a</option>
                                <option value="CASADO">Casado/a</option>
                                <option value="DIVORCIADO">Divorciado/a</option>
                                <option value="VIUDO">Viudo/a</option>
                                <option value="UNION_LIBRE">Unión Libre</option>
                              </Form.Select>
                            </Form.Group>
                          </Col>
                          <Col md={12}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-briefcase me-2"></i>
                                Profesión/Ocupación *
                              </Form.Label>
                              <Form.Control
                                type="text"
                                name="profesion"
                                value={clienteData.profesion}
                                onChange={handleClienteChange}
                                placeholder="Ej: Ingeniero, Médico, Estudiante, Comerciante"
                                required
                              />
                            </Form.Group>
                          </Col>
                        </>
                      )}

                      {/* Campos para Persona Jurídica (Cuenta Corriente) */}
                      {tipoCuenta === 'CORRIENTE' && (
                        <>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-building me-2"></i>
                                Razón Social *
                              </Form.Label>
                              <Form.Control
                                type="text"
                                name="per_nombres"
                                value={clienteData.per_nombres}
                                onChange={handleClienteChange}
                                placeholder="Nombre legal de la empresa"
                                required
                              />
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-shop me-2"></i>
                                Nombre Comercial
                              </Form.Label>
                              <Form.Control
                                type="text"
                                name="per_apellidos"
                                value={clienteData.per_apellidos}
                                onChange={handleClienteChange}
                                placeholder="Nombre comercial (opcional)"
                              />
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-file-text me-2"></i>
                                RUC de la Empresa *
                              </Form.Label>
                              <Form.Control
                                type="text"
                                name="ruc"
                                value={clienteData.ruc}
                                onChange={handleClienteChange}
                                placeholder="1234567890001"
                                minLength="13"
                                maxLength="13"
                                pattern="[0-9]{13}"
                                required
                              />
                              <Form.Text className="text-muted">
                                RUC de 13 dígitos sin espacios ni guiones
                              </Form.Text>
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-person-badge me-2"></i>
                                Representante Legal *
                              </Form.Label>
                              <Form.Control
                                type="text"
                                name="representante_legal"
                                value={clienteData.representante_legal}
                                onChange={handleClienteChange}
                                placeholder="Nombre del representante legal"
                                required
                              />
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-diagram-3 me-2"></i>
                                Tipo de Entidad *
                              </Form.Label>
                              <Form.Select
                                name="tipo_entidad"
                                value={clienteData.tipo_entidad}
                                onChange={handleClienteChange}
                                required
                              >
                                <option value="">Seleccionar tipo de empresa</option>
                                <option value="SA">Sociedad Anónima (S.A.)</option>
                                <option value="CIA_LTDA">Compañía Limitada (Cía. Ltda.)</option>
                                <option value="SAS">Sociedad por Acciones Simplificada (S.A.S.)</option>
                                <option value="UNIPERSONAL">Empresa Unipersonal</option>
                                <option value="FUNDACION">Fundación</option>
                                <option value="ONG">ONG</option>
                                <option value="OTRA">Otra</option>
                              </Form.Select>
                            </Form.Group>
                          </Col>
                          <Col md={6}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-calendar-check me-2"></i>
                                Fecha de Constitución *
                              </Form.Label>
                              <Form.Control
                                type="date"
                                name="fecha_constitucion"
                                value={clienteData.fecha_constitucion}
                                onChange={handleClienteChange}
                                max={new Date().toISOString().split('T')[0]}
                                required
                              />
                            </Form.Group>
                          </Col>
                          <Col md={12}>
                            <Form.Group>
                              <Form.Label>
                                <i className="bi bi-graph-up me-2"></i>
                                Actividad Económica Principal *
                              </Form.Label>
                              <Form.Control
                                type="text"
                                name="actividad_economica"
                                value={clienteData.actividad_economica}
                                onChange={handleClienteChange}
                                placeholder="Ej: Comercio al por menor, Servicios profesionales, Manufactura"
                                required
                              />
                            </Form.Group>
                          </Col>
                        </>
                      )}

                      {/* Campos comunes para ambos tipos */}
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>
                            <i className="bi bi-calendar-fill me-2"></i>
                            Fecha de Nacimiento {tipoCuenta === 'CORRIENTE' && '(Representante Legal)'} *
                          </Form.Label>
                          <Form.Control
                            type="date"
                            name="per_fecha_nacimiento"
                            value={clienteData.per_fecha_nacimiento}
                            onChange={handleClienteChange}
                            max={new Date().toISOString().split('T')[0]}
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>Género {tipoCuenta === 'CORRIENTE' && '(Representante Legal)'} *</Form.Label>
                          <Form.Select
                            name="per_genero"
                            value={clienteData.per_genero}
                            onChange={handleClienteChange}
                            required
                          >
                            <option value="">Selecciona el género</option>
                            <option value="Masculino">Masculino</option>
                            <option value="Femenino">Femenino</option>
                            <option value="Otro">Otro</option>
                          </Form.Select>
                        </Form.Group>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>

                {/* Información de Contacto */}
                <Card className="mb-4">
                  <Card.Header className="bg-light">
                    <h5 className="mb-0">
                      <i className="bi bi-telephone-fill me-2"></i>
                      Información de Contacto
                    </h5>
                  </Card.Header>
                  <Card.Body>
                    <Row className="g-3">
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>
                            <i className="bi bi-telephone-fill me-2"></i>
                            Teléfono *
                          </Form.Label>
                          <Form.Control
                            type="tel"
                            name="per_telefono"
                            value={clienteData.per_telefono}
                            onChange={handleClienteChange}
                            placeholder="0987654321"
                            pattern="[0-9]{10}"
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>
                            <i className="bi bi-envelope-fill me-2"></i>
                            Correo Electrónico *
                          </Form.Label>
                          <Form.Control
                            type="email"
                            name="per_correo"
                            value={clienteData.per_correo}
                            onChange={handleClienteChange}
                            placeholder="tu@email.com"
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={12}>
                        <Form.Group>
                          <Form.Label>
                            <i className="bi bi-geo-alt-fill me-2"></i>
                            Dirección *
                          </Form.Label>
                          <Form.Control
                            type="text"
                            name="per_direccion"
                            value={clienteData.per_direccion}
                            onChange={handleClienteChange}
                            placeholder="Av. Principal 123, Ciudad"
                            required
                          />
                        </Form.Group>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>

                {/* Datos de la Cuenta */}
                <Card className="mb-4">
                  <Card.Header className={tipoCuenta === 'AHORRO' ? 'bg-primary text-white' : 'bg-success text-white'}>
                    <h5 className="mb-0">
                      <i className="bi bi-bank me-2"></i>
                      Configuración de tu Cuenta {tipoCuenta === 'AHORRO' ? 'de Ahorros' : 'Corriente'}
                    </h5>
                  </Card.Header>
                  <Card.Body>
                    <Row className="g-3">
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>
                            <i className="bi bi-person-badge me-2"></i>
                            Usuario de la Cuenta *
                          </Form.Label>
                          <Form.Control
                            type="text"
                            name="cuen_usuario"
                            value={cuentaData.cuen_usuario}
                            onChange={handleCuentaChange}
                            placeholder="Nombre de usuario único"
                            minLength="4"
                            required
                          />
                          <Form.Text className="text-muted">
                            Este será tu usuario para iniciar sesión
                          </Form.Text>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>
                            <i className="bi bi-lock-fill me-2"></i>
                            Contraseña *
                          </Form.Label>
                          <Form.Control
                            type="password"
                            name="cuen_password"
                            value={cuentaData.cuen_password}
                            onChange={handleCuentaChange}
                            placeholder="Mínimo 6 caracteres"
                            minLength="6"
                            required
                          />
                          <Form.Text className="text-muted">
                            Usa una contraseña segura
                          </Form.Text>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group>
                          <Form.Label>
                            <i className="bi bi-cash me-2"></i>
                            Depósito Inicial *
                          </Form.Label>
                          <Form.Control
                            type="number"
                            step="0.01"
                            name="cuen_saldo"
                            value={cuentaData.cuen_saldo}
                            onChange={handleCuentaChange}
                            min={tipoCuenta === 'AHORRO' ? "0" : "100"}
                            required
                          />
                          <Form.Text className="text-muted">
                            {tipoCuenta === 'AHORRO' ? 'Monto mínimo: $0.00' : 'Monto mínimo: $100.00'}
                          </Form.Text>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <div className="d-flex align-items-center h-100">
                          <Alert variant={tipoCuenta === 'AHORRO' ? 'primary' : 'success'} className="mb-0 w-100">
                            <small>
                              <strong>Tipo:</strong> Cuenta {tipoCuenta === 'AHORRO' ? 'de Ahorros' : 'Corriente'}
                              <br />
                              <strong>Estado:</strong> Se activará automáticamente
                            </small>
                          </Alert>
                        </div>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>

                <div className="d-grid gap-2">
                  <Button
                    type="submit"
                    variant={tipoCuenta === 'AHORRO' ? 'primary' : 'success'}
                    size="lg"
                    disabled={loading}
                    className="py-3"
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Creando cuenta...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-circle me-2"></i>
                        Crear Cliente y Cuenta {tipoCuenta === 'AHORRO' ? 'de Ahorros' : 'Corriente'}
                      </>
                    )}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );

  return (
    <>
      {currentStep === 1 && renderStep1()}
      {currentStep === 2 && renderStep2()}
    </>
  );
}

export default Register;
