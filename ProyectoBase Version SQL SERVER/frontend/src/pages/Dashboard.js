import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Nav, Button, Table, Badge, Form, Modal, Alert } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { 
  cuentaService, 
  tarjetaService, 
  transaccionService, 
  cajeroService,
  retiroSinTarjetaService 
} from '../services/api';

function Dashboard({ user }) {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [cuentas, setCuentas] = useState([]);
  const [tarjetas, setTarjetas] = useState([]);
  const [transacciones, setTransacciones] = useState([]);
  const [movimientos, setMovimientos] = useState([]);
  const [cajeros, setCajeros] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showRetiroModal, setShowRetiroModal] = useState(false);
  const [showTarjetaModal, setShowTarjetaModal] = useState(false);
  const [showRetiroSinTarjetaModal, setShowRetiroSinTarjetaModal] = useState(false);

  // Formularios
  const [retiroForm, setRetiroForm] = useState({
    CUEN_ID: '',
    CAJ_ID: '',
    RET_MONTO: '',
    tipo_retiro: 'CON_TARJETA',
    TAR_NUMERO_TARJETA: '',
    IMPRIMIR_BOUCHER: 'SI'  // Por defecto sí imprimir
  });

  // Formulario para retiro sin tarjeta
  const [retiroSinTarjetaForm, setRetiroSinTarjetaForm] = useState({
    CUEN_ID: '',
    CAJ_ID: '',
    telefono: '',
    monto: ''
  });

  const [codigoGenerado, setCodigoGenerado] = useState('');
  const [condicionesRetiro, setCondicionesRetiro] = useState({
    disponible: false,
    monto_maximo: 300,
    horas_limite: 4,
    intentos_permitidos: 3
  });
  const [limitesDiarios, setLimitesDiarios] = useState({
    limite_diario_monto: 300,
    limite_diario_retiros: 5,
    monto_disponible: 300,
    retiros_realizados_hoy: 0,
    retiros_disponibles: 5,
    puede_retirar: true,
    mensaje: 'Límites disponibles'
  });

  const [tarjetaForm, setTarjetaForm] = useState({
    CUEN_ID: '',
    TAR_TIPO: 'DEBITO',
    TAR_ESTADO_TARJETA: 'ACTIVA',
    TAR_PIN: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Cargar cuentas del usuario autenticado
      const cuentasResponse = await cuentaService.listarPorCliente();
      setCuentas(cuentasResponse.data);

      // Cargar tarjetas del usuario autenticado
      const tarjetasResponse = await tarjetaService.listarPorCuenta();
      setTarjetas(tarjetasResponse.data);

      // Cargar cajeros
      const cajerosResponse = await cajeroService.listar();
      setCajeros(cajerosResponse.data);

      // Cargar movimientos del usuario
      try {
        const movimientosResponse = await transaccionService.obtenerMovimientos();
        setMovimientos(movimientosResponse.data.movimientos || []);
      } catch (error) {
        console.error('Error cargando movimientos:', error);
        setMovimientos([]);
      }

      // Cargar condiciones para retiro sin tarjeta
      try {
        const condicionesResponse = await retiroSinTarjetaService.obtenerCondiciones();
        setCondicionesRetiro(condicionesResponse.data);
      } catch (error) {
        console.error('Error cargando condiciones de retiro sin tarjeta:', error);
        // Mantener valores por defecto si no se pueden cargar las condiciones
      }
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Error al cargar los datos. Verifica tu conexión.', {
        position: "top-right",
        autoClose: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  const cargarLimitesDiarios = async (cuentaId) => {
    try {
      const response = await retiroSinTarjetaService.obtenerLimitesDiarios(cuentaId);
      setLimitesDiarios(response.data);
    } catch (error) {
      console.error('Error cargando límites diarios:', error);
      // Mantener valores por defecto si no se pueden cargar los límites
    }
  };

  // Función para manejar cambio de pestaña
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    
    // Si cambia a retiro sin tarjeta, cargar límites diarios
    if (tab === 'retiro-sin-tarjeta' && cuentas.length > 0) {
      const cuenta = cuentas[0]; // Usar la primera cuenta disponible
      cargarLimitesDiarios(cuenta.CUEN_ID);
    }
  };

  const handleCrearTarjeta = async (e) => {
    e.preventDefault();
    try {
      // Validaciones del frontend
      if (!tarjetaForm.CUEN_ID) {
        toast.error('Debes seleccionar una cuenta');
        return;
      }

      // PIN es requerido para todos los tipos de tarjeta según el nuevo esquema
      if (!tarjetaForm.TAR_PIN || tarjetaForm.TAR_PIN.length !== 4) {
        toast.error('El PIN debe tener exactamente 4 dígitos');
        return;
      }

      if (!/^\d{4}$/.test(tarjetaForm.TAR_PIN)) {
        toast.error('El PIN debe contener solo números');
        return;
      }

      console.log('Datos de tarjeta a enviar:', tarjetaForm);
      
      await tarjetaService.crear(tarjetaForm);
      toast.success('¡Tarjeta creada exitosamente! Ya está disponible para usar.', {
        position: "top-right",
        autoClose: 4000,
      });
      setShowTarjetaModal(false);
      setTarjetaForm({
        CUEN_ID: '',
        TAR_TIPO: 'DEBITO',
        TAR_ESTADO_TARJETA: 'ACTIVA',
        TAR_PIN: ''
      });
      loadData();
    } catch (error) {
      console.error('Error creando tarjeta:', error);
      let errorMessage = 'Error inesperado al crear la tarjeta';
      
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;
        
        console.log('Error response:', data);
        
        switch (status) {
          case 422:
            if (data.detail && Array.isArray(data.detail)) {
              const validationErrors = data.detail.map(err => {
                const field = err.loc?.[err.loc.length - 1] || 'campo';
                return `${field}: ${err.msg || 'Valor inválido'}`;
              }).join('. ');
              errorMessage = `Errores de validación: ${validationErrors}`;
            } else if (typeof data.detail === 'string') {
              errorMessage = data.detail;
            } else {
              errorMessage = 'Datos de la tarjeta no válidos.';
            }
            break;
          case 400:
            errorMessage = data.detail || 'Solicitud incorrecta. Verifica los datos.';
            break;
          case 409:
            errorMessage = data.detail || 'Ya existe una tarjeta con esas características.';
            break;
          default:
            errorMessage = data.detail || 'Error del servidor al crear la tarjeta.';
        }
      } else if (error.request) {
        errorMessage = 'No se pudo conectar con el servidor.';
      }
      
      toast.error(errorMessage, {
        position: "top-right",
        autoClose: 6000,
      });
    }
  };

  // Funciones para retiro sin tarjeta
  const generarCodigoRetiro = () => {
    return Math.floor(100000 + Math.random() * 900000).toString(); // Código de 6 dígitos
  };

  const handleGenerarCodigoRetiro = async (e) => {
    e.preventDefault();
    try {
      // Verificar si el servicio está disponible
      if (!condicionesRetiro.disponible) {
        toast.error(condicionesRetiro.mensaje || 'Servicio de retiro sin tarjeta no disponible temporalmente');
        return;
      }

      // Validaciones
      if (!retiroSinTarjetaForm.CUEN_ID) {
        toast.error('Debe seleccionar una cuenta');
        return;
      }

      if (!retiroSinTarjetaForm.CAJ_ID) {
        toast.error('Debe seleccionar un cajero');
        return;
      }

      if (!retiroSinTarjetaForm.telefono || retiroSinTarjetaForm.telefono.length !== 10) {
        toast.error('Debe ingresar un número de celular válido de 10 dígitos');
        return;
      }

      const monto = parseFloat(retiroSinTarjetaForm.monto);
      if (!monto || monto < 10 || monto > condicionesRetiro.monto_maximo) {
        toast.error(`El monto debe estar entre $10 y $${condicionesRetiro.monto_maximo}`);
        return;
      }

      if (monto % 10 !== 0) {
        toast.error('El monto debe ser múltiplo de $10');
        return;
      }

      // Verificar que la cuenta tenga saldo suficiente
      const cuentaSeleccionada = cuentas.find(c => c.CUEN_ID.toString() === retiroSinTarjetaForm.CUEN_ID);
      if (!cuentaSeleccionada) {
        toast.error('Cuenta no encontrada');
        return;
      }

      if (parseFloat(cuentaSeleccionada.CUEN_SALDO) < monto) {
        toast.error('Saldo insuficiente en la cuenta seleccionada');
        return;
      }

      // Enviar al backend para generar y guardar el código
      const response = await retiroSinTarjetaService.generarCodigo({
        CUEN_ID: parseInt(retiroSinTarjetaForm.CUEN_ID),
        CAJ_ID: parseInt(retiroSinTarjetaForm.CAJ_ID),
        telefono: retiroSinTarjetaForm.telefono,
        monto: monto
      });

      const codigo = response.data.codigo;
      setCodigoGenerado(codigo);

      // Recargar límites diarios después de generar código
      cargarLimitesDiarios(parseInt(retiroSinTarjetaForm.CUEN_ID));

      toast.success(`Código generado: ${codigo}. Válido por ${condicionesRetiro.horas_limite} horas. Diríjase al cajero para completar el retiro.`, {
        position: "top-right",
        autoClose: 10000,
      });

      // No cerrar el modal para que el usuario vea el código generado
      // setShowRetiroSinTarjetaModal(false);

    } catch (error) {
      console.error('Error generando código:', error);
      let errorMessage = 'Error al generar código de retiro';
      
      if (error.response) {
        switch (error.response.status) {
          case 400:
            errorMessage = error.response.data.detail || 'Datos inválidos';
            break;
          case 409:
            errorMessage = 'Ya tienes un código activo. Usa el código anterior o espera a que expire.';
            break;
          case 500:
            errorMessage = 'Error interno del servidor. Intenta nuevamente.';
            break;
          default:
            errorMessage = error.response.data.detail || errorMessage;
        }
      }
      
      toast.error(errorMessage);
    }
  };

  const handleRetiroSinTarjetaChange = (e) => {
    setRetiroSinTarjetaForm({
      ...retiroSinTarjetaForm,
      [e.target.name]: e.target.value
    });
  };

  const handleProcesarRetiro = async (e) => {
    e.preventDefault();
    try {
      const response = await transaccionService.procesarRetiro(retiroForm);
      toast.success('¡Retiro procesado exitosamente! El dinero ha sido dispensado.', {
        position: "top-right",
        autoClose: 4000,
      });
      setShowRetiroModal(false);
      setRetiroForm({
        CUEN_ID: '',
        CAJ_ID: '',
        RET_MONTO: '',
        tipo_retiro: 'CON_TARJETA',
        TAR_NUMERO_TARJETA: '',
        IMPRIMIR_BOUCHER: 'SI'
      });
      loadData();
    } catch (error) {
      console.error('Error procesando retiro:', error);
      let errorMessage = 'Error inesperado al procesar el retiro';
      
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;
        
        switch (status) {
          case 422:
            if (data.detail && Array.isArray(data.detail)) {
              const validationErrors = data.detail.map(err => {
                const field = err.loc?.[err.loc.length - 1] || 'campo';
                const fieldNames = {
                  'CUEN_ID': 'Cuenta seleccionada',
                  'CAJ_ID': 'Cajero seleccionado',
                  'RET_MONTO': 'Monto a retirar',
                  'TAR_NUMERO_TARJETA': 'Número de tarjeta',
                  'tipo_retiro': 'Tipo de retiro'
                };
                const friendlyField = fieldNames[field] || field;
                return `${friendlyField}: ${err.msg || 'Valor inválido'}`;
              }).join('. ');
              errorMessage = `Errores: ${validationErrors}`;
            } else {
              errorMessage = data.detail || 'Datos del retiro no válidos.';
            }
            break;
          case 400:
            if (data.detail && data.detail.includes('saldo insuficiente')) {
              errorMessage = 'Saldo insuficiente. No tienes fondos suficientes para este retiro.';
            } else if (data.detail && data.detail.includes('monto mínimo')) {
              errorMessage = 'El monto mínimo para retiro es $10.00';
            } else if (data.detail && data.detail.includes('monto máximo')) {
              errorMessage = 'El monto máximo para retiro es $600.00 por transacción.';
            } else {
              errorMessage = data.detail || 'Error en los datos del retiro.';
            }
            break;
          case 404:
            errorMessage = 'Cuenta o tarjeta no encontrada. Verifica los datos.';
            break;
          case 409:
            errorMessage = 'El cajero seleccionado no está disponible en este momento.';
            break;
          default:
            errorMessage = data.detail || 'Error del servidor al procesar el retiro.';
        }
      } else if (error.request) {
        errorMessage = 'No se pudo conectar con el servidor.';
      }
      
      toast.error(errorMessage, {
        position: "top-right",
        autoClose: 8000,
      });
    }
  };

  const renderOverview = () => (
    <Row className="g-4">
      <Col md={4}>
        <Card className="border-primary">
          <Card.Body className="text-center">
            <i className="bi bi-bank2 text-primary" style={{fontSize: '3rem'}}></i>
            <h3 className="mt-3">{cuentas.length}</h3>
            <p className="text-muted">Cuentas Activas</p>
          </Card.Body>
        </Card>
      </Col>
      <Col md={4}>
        <Card className="border-success">
          <Card.Body className="text-center">
            <i className="bi bi-credit-card text-success" style={{fontSize: '3rem'}}></i>
            <h3 className="mt-3">{tarjetas.length}</h3>
            <p className="text-muted">Tarjetas</p>
          </Card.Body>
        </Card>
      </Col>
      <Col md={4}>
        <Card className="border-info">
          <Card.Body className="text-center">
            <i className="bi bi-cash-coin text-info" style={{fontSize: '3rem'}}></i>
            <h3 className="mt-3">
              ${cuentas.reduce((total, cuenta) => total + parseFloat(cuenta.CUEN_SALDO || 0), 0).toFixed(2)}
            </h3>
            <p className="text-muted">Saldo Total</p>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );

  const renderCuentas = () => (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4>Mis Cuentas</h4>
      </div>
      <div className="alert alert-info mb-3">
        <i className="bi bi-info-circle me-2"></i>
        Estas son tus cuentas bancarias activas. Para crear nuevas cuentas, contacta a nuestras sucursales.
      </div>
      <Table responsive striped>
        <thead>
          <tr>
            <th>Número de Cuenta</th>
            <th>Tipo</th>
            <th>Saldo</th>
            <th>Estado</th>
            <th>Usuario</th>
          </tr>
        </thead>
        <tbody>
          {cuentas.map(cuenta => (
            <tr key={cuenta.CUEN_ID}>
              <td className="font-monospace">{cuenta.CUEN_NUMERO_CUENTA}</td>
              <td>
                <Badge bg={cuenta.CUEN_TIPO === 'AHORRO' ? 'info' : 'warning'}>
                  {cuenta.CUEN_TIPO}
                </Badge>
              </td>
              <td className="fw-bold">${parseFloat(cuenta.CUEN_SALDO).toFixed(2)}</td>
              <td>
                <Badge bg={cuenta.CUEN_ESTADO === 'ACTIVA' ? 'success' : 'danger'}>
                  {cuenta.CUEN_ESTADO}
                </Badge>
              </td>
              <td>{cuenta.CUEN_USUARIO}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );

  const renderTarjetas = () => (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4>Mis Tarjetas</h4>
        <Button variant="primary" onClick={() => setShowTarjetaModal(true)}>
          <i className="bi bi-plus-circle me-2"></i>
          Nueva Tarjeta
        </Button>
      </div>
      <Row>
        {tarjetas.map(tarjeta => (
          <Col md={6} lg={4} key={tarjeta.TAR_ID} className="mb-4">
            <Card className="border-0 shadow">
              <Card.Body style={{
                background: tarjeta.TAR_TIPO === 'CREDITO' ? 
                  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 
                  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                color: 'white'
              }}>
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <h6 className="mb-1">Banco Pichincha</h6>
                    <small>{tarjeta.TAR_TIPO}</small>
                  </div>
                  <i className="bi bi-credit-card" style={{fontSize: '1.5rem'}}></i>
                </div>
                <div className="mt-3">
                  <div className="font-monospace h5 mb-2">
                    {tarjeta.TAR_NUMERO_TARJETA}
                  </div>
                  <div className="d-flex justify-content-between">
                    <small>
                      Válida hasta: {new Date(tarjeta.TAR_FECHA_EXPIRACION).toLocaleDateString()}
                    </small>
                    <Badge bg={tarjeta.TAR_ESTADO === 'ACTIVA' ? 'success' : 'danger'} className="ms-2">
                      {tarjeta.TAR_ESTADO}
                    </Badge>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </>
  );

  const renderMovimientos = () => (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4>
          <i className="bi bi-arrow-left-right me-2"></i>
          Movimientos
        </h4>
        <Badge bg="info" className="fs-6">
          {movimientos.length} movimientos
        </Badge>
      </div>

      {movimientos.length === 0 ? (
        <Alert variant="info" className="text-center">
          <i className="bi bi-info-circle me-2"></i>
          No tienes movimientos registrados aún.
        </Alert>
      ) : (
        <Table responsive striped>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Tipo</th>
              <th>Monto</th>
              <th>Método</th>
              <th>Estado</th>
              <th>Tarjeta</th>
              <th>Cajero</th>
              <th>N° Transacción</th>
            </tr>
          </thead>
          <tbody>
            {movimientos.map((movimiento) => (
              <tr key={movimiento.id}>
                <td>
                  <small>
                    {new Date(movimiento.fecha).toLocaleDateString('es-ES', {
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </small>
                </td>
                <td>
                  <Badge bg="primary">
                    <i className="bi bi-cash me-1"></i>
                    {movimiento.tipo_movimiento}
                  </Badge>
                </td>
                <td>
                  <strong className="text-success">
                    ${movimiento.monto.toLocaleString('es-ES', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2
                    })}
                  </strong>
                </td>
                <td>
                  <Badge bg={movimiento.metodo === 'CON TARJETA' ? 'success' : 'warning'}>
                    {movimiento.metodo}
                  </Badge>
                </td>
                <td>
                  {movimiento.metodo === 'SIN TARJETA' && movimiento.estado_codigo ? (
                    <Badge bg={movimiento.estado_codigo === 'USADO' ? 'success' : 'secondary'}>
                      {movimiento.estado_codigo}
                    </Badge>
                  ) : movimiento.metodo === 'CON TARJETA' ? (
                    <Badge bg="success">
                      COMPLETADO
                    </Badge>
                  ) : (
                    <Badge bg="secondary">
                      N/A
                    </Badge>
                  )}
                </td>
                <td>
                  {movimiento.tarjeta ? (
                    <div>
                      <small className="text-muted">{movimiento.tarjeta.numero}</small>
                      <br />
                      <Badge bg={movimiento.tarjeta.tipo === 'DÉBITO' ? 'info' : 'warning'} pill>
                        {movimiento.tarjeta.tipo}
                      </Badge>
                    </div>
                  ) : (
                    <small className="text-muted">Sin tarjeta</small>
                  )}
                </td>
                <td>
                  <small>
                    <strong>{movimiento.cajero.ubicacion}</strong>
                    <br />
                    <span className="text-muted">{movimiento.cajero.tipo}</span>
                  </small>
                </td>
                <td>
                  <small className="text-muted">
                    {movimiento.numero_transaccion || 'N/A'}
                  </small>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </>
  );

  const renderRetiroSinTarjeta = () => (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4>
          <i className="bi bi-phone me-2"></i>
          Retiro sin Tarjeta
        </h4>
        <Button variant="success" onClick={() => setShowRetiroSinTarjetaModal(true)}>
          <i className="bi bi-qr-code me-2"></i>
          Generar Código
        </Button>
      </div>

      <Row>
        <Col lg={8}>
          <Card className="border-0 shadow">
            <Card.Header className="bg-success text-white">
              <h5 className="mb-0">
                <i className="bi bi-info-circle me-2"></i>
                ¿Cómo funciona?
              </h5>
            </Card.Header>
            <Card.Body>
              <div className="row">
                <div className="col-md-4 text-center mb-3">
                  <div className="mb-3">
                    <i className="bi bi-1-circle text-success" style={{fontSize: '3rem'}}></i>
                  </div>
                  <h6>Generar Código</h6>
                  <p className="text-muted small">
                    Desde tu dashboard genera un código de 6 dígitos
                  </p>
                </div>
                <div className="col-md-4 text-center mb-3">
                  <div className="mb-3">
                    <i className="bi bi-2-circle text-success" style={{fontSize: '3rem'}}></i>
                  </div>
                  <h6>Ir al Cajero</h6>
                  <p className="text-muted small">
                    Diríjase a cualquier cajero Banco Pichincha
                  </p>
                </div>
                <div className="col-md-4 text-center mb-3">
                  <div className="mb-3">
                    <i className="bi bi-3-circle text-success" style={{fontSize: '3rem'}}></i>
                  </div>
                  <h6>Ingresar Código</h6>
                  <p className="text-muted small">
                    Selecciona retiro sin tarjeta e ingresa tu código
                  </p>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="border-0 shadow">
            <Card.Header className="bg-info text-white">
              <h6 className="mb-0">
                <i className="bi bi-shield-check me-2"></i>
                Información Importante
              </h6>
            </Card.Header>
            <Card.Body>
              <ul className="list-unstyled mb-0">
                <li className="mb-2">
                  <i className="bi bi-check-circle text-success me-2"></i>
                  <small>Retiros de $10 a $500</small>
                </li>
                <li className="mb-2">
                  <i className="bi bi-clock text-warning me-2"></i>
                  <small>Código válido por 4 horas</small>
                </li>
                <li className="mb-2">
                  <i className="bi bi-phone text-info me-2"></i>
                  <small>Requiere número de celular</small>
                </li>
                <li className="mb-0">
                  <i className="bi bi-bank text-primary me-2"></i>
                  <small>Disponible 24/7</small>
                </li>
              </ul>
            </Card.Body>
          </Card>

          <Card className="border-0 shadow mt-3">
            <Card.Header className="bg-warning text-dark">
              <h6 className="mb-0">
                <i className="bi bi-exclamation-triangle me-2"></i>
                Límites Diarios
              </h6>
            </Card.Header>
            <Card.Body>
              <div className="row text-center">
                <div className="col-6">
                  <div className="border-end">
                    <h5 className="text-warning mb-1">
                      ${(300 - (limitesDiarios?.monto_disponible || 300)).toFixed(0)}
                    </h5>
                    <small className="text-muted">de $300</small>
                    <div className="progress mt-2" style={{height: '6px'}}>
                      <div 
                        className="progress-bar bg-warning" 
                        style={{width: `${((300 - (limitesDiarios?.monto_disponible || 300)) / 300) * 100}%`}}
                      ></div>
                    </div>
                    <small className="text-success">
                      ${limitesDiarios?.monto_disponible || 300} disponible
                    </small>
                  </div>
                </div>
                <div className="col-6">
                  <h5 className="text-warning mb-1">{limitesDiarios?.retiros_realizados_hoy || 0}</h5>
                  <small className="text-muted">de 5 retiros</small>
                  <div className="progress mt-2" style={{height: '6px'}}>
                    <div 
                      className="progress-bar bg-warning" 
                      style={{width: `${((limitesDiarios?.retiros_realizados_hoy || 0) / 5) * 100}%`}}
                    ></div>
                  </div>
                  <small className="text-success">
                    {limitesDiarios?.retiros_disponibles || 5} disponibles
                  </small>
                </div>
              </div>
              <div className="text-center mt-2">
                <small className="text-muted">
                  <i className="bi bi-calendar-day me-1"></i>
                  Límites reinician diariamente
                </small>
              </div>
              {limitesDiarios?.mensaje && (
                <div className="text-center mt-2">
                  <small className={`${limitesDiarios.puede_retirar ? 'text-success' : 'text-danger'}`}>
                    <i className={`bi ${limitesDiarios.puede_retirar ? 'bi-check-circle' : 'bi-exclamation-circle'} me-1`}></i>
                    {limitesDiarios.mensaje}
                  </small>
                </div>
              )}
            </Card.Body>
          </Card>

          {codigoGenerado && (
            <Card className="border-success mt-3">
              <Card.Header className="bg-success text-white text-center">
                <h6 className="mb-0">
                  <i className="bi bi-qr-code me-2"></i>
                  Código Generado
                </h6>
              </Card.Header>
              <Card.Body className="text-center">
                <h2 className="text-success mb-3">{codigoGenerado}</h2>
                <p className="text-muted small mb-0">
                  <i className="bi bi-clock me-1"></i>
                  Válido por 4 horas
                </p>
                <Button 
                  variant="outline-success" 
                  size="sm" 
                  className="mt-2"
                  onClick={() => setCodigoGenerado('')}
                >
                  Cerrar
                </Button>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </>
  );

  const renderRetiros = () => (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4>Retiros</h4>
        <Button variant="primary" onClick={() => setShowRetiroModal(true)}>
          <i className="bi bi-cash-coin me-2"></i>
          Nuevo Retiro
        </Button>
      </div>
      <Card>
        <Card.Body>
          <div className="text-center py-5">
            <i className="bi bi-cash-coin text-muted" style={{fontSize: '4rem'}}></i>
            <h5 className="mt-3 text-muted">Realiza retiros desde cualquier cajero</h5>
            <p className="text-muted">
              Utiliza tus tarjetas o realiza retiros sin tarjeta con tu código de seguridad
            </p>
          </div>
        </Card.Body>
      </Card>
    </>
  );

  return (
    <Container fluid className="py-4">
      <Row>
        <Col md={3}>
          <Card className="sidebar">
            <Card.Header>
              <h5 className="mb-0 text-pichincha-blue">
                <i className="bi bi-person-circle me-2"></i>
                Panel de Control
              </h5>
            </Card.Header>
            <Card.Body className="p-0">
              <Nav variant="pills" className="flex-column">
                <Nav.Item>
                  <Nav.Link 
                    active={activeTab === 'overview'} 
                    onClick={() => handleTabChange('overview')}
                    className="rounded-0 border-bottom"
                  >
                    <i className="bi bi-speedometer2 me-2"></i>
                    Resumen
                  </Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link 
                    active={activeTab === 'cuentas'} 
                    onClick={() => handleTabChange('cuentas')}
                    className="rounded-0 border-bottom"
                  >
                    <i className="bi bi-bank me-2"></i>
                    Cuentas
                  </Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link 
                    active={activeTab === 'tarjetas'} 
                    onClick={() => handleTabChange('tarjetas')}
                    className="rounded-0 border-bottom"
                  >
                    <i className="bi bi-credit-card me-2"></i>
                    Tarjetas
                  </Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link 
                    active={activeTab === 'movimientos'} 
                    onClick={() => handleTabChange('movimientos')}
                    className="rounded-0 border-bottom"
                  >
                    <i className="bi bi-arrow-left-right me-2"></i>
                    Movimientos
                  </Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link 
                    active={activeTab === 'retiro-sin-tarjeta'} 
                    onClick={() => handleTabChange('retiro-sin-tarjeta')}
                    className="rounded-0 border-bottom"
                  >
                    <i className="bi bi-phone me-2"></i>
                    Retiro sin Tarjeta
                  </Nav.Link>
                </Nav.Item>
                <Nav.Item>
                  <Nav.Link 
                    href="/cajero"
                    className="rounded-0"
                  >
                    <i className="bi bi-pc-display me-2"></i>
                    Cajero ATM
                  </Nav.Link>
                </Nav.Item>
              </Nav>
            </Card.Body>
          </Card>
        </Col>
        <Col md={9}>
          <Card>
            <Card.Header>
              <h4 className="mb-0 text-pichincha-blue">
                Bienvenido, {user.nombre || user.usuario}
              </h4>
            </Card.Header>
            <Card.Body>
              {loading ? (
                <div className="text-center py-5">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Cargando...</span>
                  </div>
                </div>
              ) : (
                <>
                  {activeTab === 'overview' && renderOverview()}
                  {activeTab === 'cuentas' && renderCuentas()}
                  {activeTab === 'tarjetas' && renderTarjetas()}
                  {activeTab === 'movimientos' && renderMovimientos()}
                  {activeTab === 'retiro-sin-tarjeta' && renderRetiroSinTarjeta()}
                </>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modal Nueva Tarjeta */}
      <Modal show={showTarjetaModal} onHide={() => setShowTarjetaModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Nueva Tarjeta</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleCrearTarjeta}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Cuenta</Form.Label>
              <Form.Select
                value={tarjetaForm.CUEN_ID}
                onChange={(e) => {
                  const cuentaSeleccionada = cuentas.find(c => c.CUEN_ID === parseInt(e.target.value));
                  setTarjetaForm({
                    ...tarjetaForm, 
                    CUEN_ID: e.target.value,
                    // Si es cuenta de ahorro, forzar a débito
                    TAR_TIPO: cuentaSeleccionada?.CUEN_TIPO === 'AHORRO' ? 'DEBITO' : tarjetaForm.TAR_TIPO
                  });
                }}
                required
              >
                <option value="">Selecciona una cuenta</option>
                {cuentas.map(cuenta => (
                  <option key={cuenta.CUEN_ID} value={cuenta.CUEN_ID}>
                    {cuenta.CUEN_NUMERO_CUENTA} - {cuenta.CUEN_TIPO} (${parseFloat(cuenta.CUEN_SALDO).toFixed(2)})
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Tipo de Tarjeta</Form.Label>
              <Form.Select
                value={tarjetaForm.TAR_TIPO}
                onChange={(e) => setTarjetaForm({...tarjetaForm, TAR_TIPO: e.target.value})}
                disabled={(() => {
                  const cuentaSeleccionada = cuentas.find(c => c.CUEN_ID === parseInt(tarjetaForm.CUEN_ID));
                  return cuentaSeleccionada?.CUEN_TIPO === 'AHORRO';
                })()}
              >
                <option value="DEBITO">Débito</option>
                <option value="CREDITO">Crédito</option>
              </Form.Select>
              {(() => {
                const cuentaSeleccionada = cuentas.find(c => c.CUEN_ID === parseInt(tarjetaForm.CUEN_ID));
                if (cuentaSeleccionada?.CUEN_TIPO === 'AHORRO') {
                  return (
                    <Form.Text className="text-info">
                      <i className="bi bi-info-circle me-1"></i>
                      Las cuentas de ahorro solo permiten tarjetas de débito
                    </Form.Text>
                  );
                }
                return null;
              })()}
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>
                <i className="bi bi-shield-lock me-2"></i>
                PIN de la Tarjeta *
              </Form.Label>
              <Form.Control
                type="password"
                value={tarjetaForm.TAR_PIN}
                onChange={(e) => setTarjetaForm({...tarjetaForm, TAR_PIN: e.target.value})}
                placeholder="Ingresa 4 dígitos"
                maxLength="4"
                pattern="[0-9]{4}"
                required
              />
              <Form.Text className="text-muted">
                PIN de 4 dígitos para usar la tarjeta
              </Form.Text>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowTarjetaModal(false)}>
              Cancelar
            </Button>
            <Button type="submit" variant="primary">
              Crear Tarjeta
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Modal Retiro */}
      <Modal show={showRetiroModal} onHide={() => setShowRetiroModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Procesar Retiro</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleProcesarRetiro}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Cuenta</Form.Label>
              <Form.Select
                value={retiroForm.CUEN_ID}
                onChange={(e) => setRetiroForm({...retiroForm, CUEN_ID: e.target.value})}
                required
              >
                <option value="">Selecciona una cuenta</option>
                {cuentas.map(cuenta => (
                  <option key={cuenta.CUEN_ID} value={cuenta.CUEN_ID}>
                    {cuenta.CUEN_NUMERO_CUENTA} - ${parseFloat(cuenta.CUEN_SALDO).toFixed(2)}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Cajero</Form.Label>
              <Form.Select
                value={retiroForm.CAJ_ID}
                onChange={(e) => setRetiroForm({...retiroForm, CAJ_ID: e.target.value})}
                required
              >
                <option value="">Selecciona un cajero</option>
                {cajeros.filter(c => c.CAJ_ESTADO === 'Activo').map(cajero => (
                  <option key={cajero.CAJ_ID} value={cajero.CAJ_ID}>
                    {cajero.CAJ_UBICACION}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Monto</Form.Label>
              <Form.Control
                type="number"
                step="0.01"
                value={retiroForm.RET_MONTO}
                onChange={(e) => setRetiroForm({...retiroForm, RET_MONTO: e.target.value})}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Tipo de Retiro</Form.Label>
              <Form.Select
                value={retiroForm.tipo_retiro}
                onChange={(e) => setRetiroForm({...retiroForm, tipo_retiro: e.target.value})}
              >
                <option value="CON_TARJETA">Con Tarjeta</option>
                <option value="SIN_TARJETA">Sin Tarjeta</option>
              </Form.Select>
            </Form.Group>
            {retiroForm.tipo_retiro === 'CON_TARJETA' && (
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Número de Tarjeta</Form.Label>
                  <Form.Select
                    value={retiroForm.TAR_NUMERO_TARJETA}
                    onChange={(e) => setRetiroForm({...retiroForm, TAR_NUMERO_TARJETA: e.target.value})}
                    required
                  >
                    <option value="">Selecciona una tarjeta</option>
                    {tarjetas.filter(t => t.TAR_ESTADO_TARJETA === 'ACTIVA').map(tarjeta => (
                      <option key={tarjeta.TAR_ID} value={tarjeta.TAR_NUMERO_TARJETA}>
                        {tarjeta.TAR_NUMERO_TARJETA} - {tarjeta.TAR_TIPO}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>¿Imprimir Boucher?</Form.Label>
                  <Form.Select
                    value={retiroForm.IMPRIMIR_BOUCHER}
                    onChange={(e) => setRetiroForm({...retiroForm, IMPRIMIR_BOUCHER: e.target.value})}
                  >
                    <option value="SI">Sí, imprimir boucher</option>
                    <option value="NO">No imprimir</option>
                  </Form.Select>
                  <Form.Text className="text-muted">
                    El boucher incluye detalles de la transacción (costo adicional: $0.36)
                  </Form.Text>
                </Form.Group>
              </>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowRetiroModal(false)}>
              Cancelar
            </Button>
            <Button type="submit" variant="primary">
              Procesar Retiro
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Modal Retiro Sin Tarjeta */}
      <Modal show={showRetiroSinTarjetaModal} onHide={() => setShowRetiroSinTarjetaModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-phone me-2"></i>
            Generar Código de Retiro Sin Tarjeta
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleGenerarCodigoRetiro}>
          <Modal.Body>
            {/* Mostrar condiciones del servicio */}
            {condicionesRetiro.disponible ? (
              <Alert variant="info" className="mb-3">
                <strong>Condiciones del servicio:</strong>
                <ul className="mb-0 mt-2">
                  <li>Monto máximo: ${condicionesRetiro.monto_maximo}</li>
                  <li>Código válido por: {condicionesRetiro.horas_limite} horas</li>
                  <li>Intentos permitidos: {condicionesRetiro.intentos_permitidos}</li>
                </ul>
              </Alert>
            ) : (
              <Alert variant="warning" className="mb-3">
                <strong>Servicio no disponible:</strong> {condicionesRetiro.mensaje || 'Temporalmente fuera de servicio'}
              </Alert>
            )}
            
            <Row>
              <Col md={8}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    <i className="bi bi-bank me-2"></i>
                    Cuenta para Retiro
                  </Form.Label>
                  <Form.Select
                    value={retiroSinTarjetaForm.CUEN_ID}
                    onChange={handleRetiroSinTarjetaChange}
                    name="CUEN_ID"
                    required
                    disabled={!condicionesRetiro.disponible}
                  >
                    <option value="">Selecciona una cuenta</option>
                    {cuentas.map(cuenta => (
                      <option key={cuenta.CUEN_ID} value={cuenta.CUEN_ID}>
                        {cuenta.CUEN_NUMERO_CUENTA} - {cuenta.CUEN_TIPO} (Disponible: ${parseFloat(cuenta.CUEN_SALDO).toFixed(2)})
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>
                    <i className="bi bi-geo-alt me-2"></i>
                    Cajero para Retiro
                  </Form.Label>
                  <Form.Select
                    value={retiroSinTarjetaForm.CAJ_ID}
                    onChange={handleRetiroSinTarjetaChange}
                    name="CAJ_ID"
                    required
                    disabled={!condicionesRetiro.disponible}
                  >
                    <option value="">Selecciona un cajero</option>
                    {cajeros.filter(c => c.CAJ_ESTADO === 'Activo').map(cajero => (
                      <option key={cajero.CAJ_ID} value={cajero.CAJ_ID}>
                        {cajero.CAJ_UBICACION} - {cajero.CAJ_SUCURSAL}
                      </option>
                    ))}
                  </Form.Select>
                  <Form.Text className="text-muted">
                    Selecciona el cajero donde realizarás el retiro
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>
                    <i className="bi bi-phone me-2"></i>
                    Número de Celular
                  </Form.Label>
                  <Form.Control
                    type="tel"
                    value={retiroSinTarjetaForm.telefono}
                    onChange={handleRetiroSinTarjetaChange}
                    name="telefono"
                    placeholder="0987654321"
                    pattern="[0-9]{10}"
                    maxLength="10"
                    required
                    disabled={!condicionesRetiro.disponible}
                  />
                  <Form.Text className="text-muted">
                    Ingresa tu número de celular de 10 dígitos
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>
                    <i className="bi bi-cash me-2"></i>
                    Monto a Retirar
                  </Form.Label>
                  <Form.Control
                    type="number"
                    value={retiroSinTarjetaForm.monto}
                    onChange={handleRetiroSinTarjetaChange}
                    name="monto"
                    min="10"
                    max={condicionesRetiro.monto_maximo}
                    step="5"
                    required
                    disabled={!condicionesRetiro.disponible}
                  />
                  <Form.Text className="text-muted">
                    Monto entre $10 y ${condicionesRetiro.monto_maximo} (múltiplos de $5)
                  </Form.Text>
                </Form.Group>

                {codigoGenerado && (
                  <Alert variant="success" className="mt-3">
                    <Alert.Heading>
                      <i className="bi bi-check-circle me-2"></i>
                      ¡Código Generado Exitosamente!
                    </Alert.Heading>
                    <div className="text-center my-3">
                      <div className="bg-light p-3 rounded border">
                        <h2 className="text-primary mb-0 font-monospace">
                          {codigoGenerado}
                        </h2>
                      </div>
                    </div>
                    <hr />
                    <p className="mb-1">
                      <strong>Celular:</strong> {retiroSinTarjetaForm.telefono}
                    </p>
                    <p className="mb-1">
                      <strong>Monto:</strong> ${retiroSinTarjetaForm.monto}
                    </p>
                    <p className="mb-1">
                      <strong>Válido por:</strong> 4 horas
                    </p>
                    <p className="mb-0 text-warning">
                      <i className="bi bi-exclamation-triangle me-1"></i>
                      Usa este código en cualquier cajero Banco Pichincha
                    </p>
                  </Alert>
                )}
              </Col>
              
              <Col md={4}>
                <Card className="bg-light">
                  <Card.Body>
                    <h6>
                      <i className="bi bi-info-circle me-2"></i>
                      Información Importante
                    </h6>
                    <ul className="small mb-0">
                      <li>Monto mínimo: $10</li>
                      <li>Monto máximo: ${condicionesRetiro.monto_maximo}</li>
                      <li>Solo múltiplos de $5</li>
                      <li>Código válido por {condicionesRetiro.horas_limite} horas</li>
                      <li>Máximo {condicionesRetiro.intentos_permitidos} intentos</li>
                      <li>Un solo uso por código</li>
                      <li>Disponible en cajeros seleccionados</li>
                    </ul>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => {
              setShowRetiroSinTarjetaModal(false);
              setCodigoGenerado('');
              setRetiroSinTarjetaForm({
                CUEN_ID: '',
                CAJ_ID: '',
                telefono: '',
                monto: ''
              });
            }}>
              {codigoGenerado ? 'Cerrar' : 'Cancelar'}
            </Button>
            {!codigoGenerado && (
              <Button 
                type="submit" 
                variant="primary"
                disabled={!condicionesRetiro.disponible || !retiroSinTarjetaForm.CUEN_ID || !retiroSinTarjetaForm.CAJ_ID || !retiroSinTarjetaForm.telefono || !retiroSinTarjetaForm.monto}
              >
                <i className="bi bi-qr-code me-2"></i>
                {condicionesRetiro.disponible ? 'Generar Código' : 'Servicio No Disponible'}
              </Button>
            )}
            {codigoGenerado && (
              <Button 
                variant="success" 
                onClick={() => {
                  setShowRetiroSinTarjetaModal(false);
                  setCodigoGenerado('');
                  setRetiroSinTarjetaForm({
                    CUEN_ID: '',
                    CAJ_ID: '',
                    telefono: '',
                    monto: ''
                  });
                }}
              >
                <i className="bi bi-check-circle me-2"></i>
                Ir al Cajero
              </Button>
            )}
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
}

export default Dashboard;
