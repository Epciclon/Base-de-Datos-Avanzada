import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar respuestas
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('userData');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Servicios de Cliente
export const clienteService = {
  crear: (data) => api.post('/api/clientes/', data),
  obtener: (id) => api.get(`/api/clientes/${id}`),
  listar: () => api.get('/api/clientes/'),
};

// Servicios de Cuenta
export const cuentaService = {
  crear: (data) => {
    const { per_id, cli_id, ...cuentaData } = data;
    if (data.CUEN_TIPO === 'AHORRO') {
      return api.post(`/api/cuentas/ahorro?per_id=${per_id}&cli_id=${cli_id}`, cuentaData);
    } else {
      return api.post(`/api/cuentas/corriente?per_id=${per_id}&cli_id=${cli_id}`, cuentaData);
    }
  },
  obtener: (id) => api.get(`/api/cuentas/${id}`),
  listarPorCliente: () => api.get(`/api/cuentas/mis-cuentas`), // Usar endpoint autenticado
  consultarSaldo: () => api.get('/api/cuentas/saldo'),
};

// Servicios de Tarjeta
export const tarjetaService = {
  crear: (data) => api.post('/api/tarjetas/', data),
  obtener: (id) => api.get(`/api/tarjetas/${id}`),
  listarPorCuenta: (cuentaId) => api.get(`/api/tarjetas/mis-tarjetas`), // Usar endpoint autenticado
  validarTarjeta: (data) => api.post('/api/cajero/validar', {
    numero_tarjeta: data.TAR_NUMERO_TARJETA,
    pin: data.TAR_PIN
  }), // Usar endpoint del cajero
};

// Servicios de Transacciones
export const transaccionService = {
  listarPorCliente: (clienteId) => api.get(`/api/transacciones/mis-transacciones`), // Usar endpoint autenticado
  procesarRetiro: (data) => api.post('/api/retiros-con-tarjeta/procesar', data),  // Nuevo endpoint
  historialPorCuenta: (cuentaId) => api.get(`/api/transacciones/cuenta/${cuentaId}`),
  obtenerMovimientos: (limit = 50) => api.get(`/api/transacciones/movimientos?limit=${limit}`),
};

// Servicios de Retiro Sin Tarjeta
export const retiroSinTarjetaService = {
  generarCodigo: (data) => api.post('/api/retiros-sin-tarjeta/generar-codigo', data),
  validarCodigo: (data) => api.post('/api/retiros-sin-tarjeta/validar-codigo', data),
  procesarRetiro: (codigo_id) => api.post('/api/retiros-sin-tarjeta/procesar-retiro', null, { 
    params: { codigo_id } 
  }),
  marcarCodigoNoUsado: (data) => api.post('/api/retiros-sin-tarjeta/marcar-codigo-no-usado', data),
  misCodigos: () => api.get('/api/retiros-sin-tarjeta/mis-codigos'),
  obtenerCondiciones: () => api.get('/api/retiros-sin-tarjeta/condiciones'),
  obtenerLimitesDiarios: (cuentaId) => api.get(`/api/retiros-sin-tarjeta/limites-diarios/${cuentaId}`),
};

// Servicios de Cajero
export const cajeroService = {
  listar: () => api.get('/api/cajeros/'),
  obtener: (id) => api.get(`/api/cajeros/${id}`),
};

// Servicios de Autenticación
export const authService = {
  login: (usuario, password) => 
    api.post('/api/auth/login', { usuario, password }),
  register: (data) => api.post('/api/auth/register', data),
};

export default api;
