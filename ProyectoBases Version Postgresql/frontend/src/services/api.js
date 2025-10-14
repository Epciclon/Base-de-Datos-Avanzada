import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://backend-nine-mu-43.vercel.app/api';

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
  crear: (data) => api.post('/clientes/', data),
  obtener: (id) => api.get(`/clientes/${id}`),
  listar: () => api.get('/clientes/'),
};

// Servicios de Cuenta
export const cuentaService = {
  crear: (data) => {
    const { per_id, cli_id, ...cuentaData } = data;
    if (data.cuen_tipo === 'AHORRO') {
      return api.post(`/cuentas/ahorro?per_id=${per_id}&cli_id=${cli_id}`, cuentaData);
    } else {
      return api.post(`/cuentas/corriente?per_id=${per_id}&cli_id=${cli_id}`, cuentaData);
    }
  },
  obtener: (id) => api.get(`/cuentas/${id}`),
  listarPorCliente: () => api.get(`/cuentas/mis-cuentas`), // Usar endpoint autenticado
  consultarSaldo: () => api.get('/cuentas/saldo'),
};

// Servicios de Tarjeta
export const tarjetaService = {
  crear: (data) => api.post('/tarjetas/', data),
  obtener: (id) => api.get(`/tarjetas/${id}`),
  listarPorCuenta: (cuentaId) => api.get(`/tarjetas/mis-tarjetas`), // Usar endpoint autenticado
  validarTarjeta: (data) => api.post('/cajero/validar', {
    numero_tarjeta: data.tar_numero_tarjeta,
    pin: data.tar_pin
  }), // Usar endpoint del cajero
};

// Servicios de Transacciones
export const transaccionService = {
  listarPorCliente: (clienteId) => api.get(`/transacciones/mis-transacciones`), // Usar endpoint autenticado
  procesarRetiro: (data) => api.post('/retiros-con-tarjeta/procesar', data),  // Nuevo endpoint
  historialPorCuenta: (cuentaId) => api.get(`/transacciones/cuenta/${cuentaId}`),
  obtenerMovimientos: (limit = 50) => api.get(`/transacciones/movimientos?limit=${limit}`),
};

// Servicios de Retiro Sin Tarjeta
export const retiroSinTarjetaService = {
  generarCodigo: (data) => api.post('/retiros-sin-tarjeta/generar-codigo', data),
  validarCodigo: (data) => api.post('/retiros-sin-tarjeta/validar-codigo', data),
  procesarRetiro: (codigo_id) => api.post('/retiros-sin-tarjeta/procesar-retiro', null, { 
    params: { codigo_id } 
  }),
  marcarCodigoNoUsado: (data) => api.post('/retiros-sin-tarjeta/marcar-codigo-no-usado', data),
  misCodigos: () => api.get('/retiros-sin-tarjeta/mis-codigos'),
  obtenerCondiciones: () => api.get('/retiros-sin-tarjeta/condiciones'),
  obtenerLimitesDiarios: (cuentaId) => api.get(`/retiros-sin-tarjeta/limites-diarios/${cuentaId}`),
};

// Servicios de Cajero
export const cajeroService = {
  listar: () => api.get('/cajeros/'),
  obtener: (id) => api.get(`/cajeros/${id}`),
};

// Servicios de Autenticación
export const authService = {
  login: (usuario, password) => 
    api.post('/auth/login', { usuario, password }),
  register: (data) => api.post('/auth/register', data),
};

export default api;
