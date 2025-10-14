import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { authService } from '../services/api';
import { useNavigate } from 'react-router-dom';

function Login({ onLogin }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    usuario: '',
    password: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Validaciones básicas del frontend
      if (!formData.usuario.trim()) {
        toast.error('El campo Usuario es obligatorio');
        setLoading(false);
        return;
      }
      
      if (!formData.password.trim()) {
        toast.error('El campo Contraseña es obligatorio');
        setLoading(false);
        return;
      }

      const response = await authService.login(formData.usuario, formData.password);
      const { access_token, usuario, cuenta_id } = response.data;
      
      // Crear objeto cuenta_info para compatibilidad con el dashboard
      const cuenta_info = {
        usuario: usuario,
        cuenta_id: cuenta_id
      };
      
      toast.success('¡Bienvenido al Banco Pichincha! Inicio de sesión exitoso', {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      
      // Guardar datos en localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('userData', JSON.stringify(cuenta_info));
      
      // Actualizar el estado del usuario en App.js
      onLogin(cuenta_info);
      
      navigate('/dashboard');
      
    } catch (error) {
      console.error('Error de login:', error);
      
      let errorMessage = 'Error inesperado al iniciar sesión';
      
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;
        
        switch (status) {
          case 401:
            errorMessage = 'Credenciales incorrectas. Verifica tu usuario y contraseña.';
            break;
            
          case 422:
            if (data.detail && Array.isArray(data.detail)) {
              const validationErrors = data.detail.map(err => err.msg || 'Datos inválidos').join('. ');
              errorMessage = `Errores en los datos: ${validationErrors}`;
            } else {
              errorMessage = data.detail || 'Datos de acceso no válidos.';
            }
            break;
            
          case 404:
            errorMessage = 'Usuario no encontrado. Verifica que estés registrado en el sistema.';
            break;
            
          case 403:
            errorMessage = 'Acceso denegado. Tu cuenta puede estar inactiva.';
            break;
            
          case 500:
            errorMessage = 'Error interno del servidor. Intenta nuevamente más tarde.';
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
        autoClose: 6000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col md={6} lg={4}>
          <Card className="shadow">
            <Card.Header className="bg-primary text-white text-center">
              <h3 className="mb-0">
                <i className="bi bi-box-arrow-in-right me-2"></i>
                Iniciar Sesión
              </h3>
            </Card.Header>
            <Card.Body className="p-4">
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    <i className="bi bi-person-fill me-2"></i>
                    Usuario
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="usuario"
                    value={formData.usuario}
                    onChange={handleChange}
                    placeholder="Ingresa tu usuario"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>
                    <i className="bi bi-lock-fill me-2"></i>
                    Contraseña
                  </Form.Label>
                  <Form.Control
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Ingresa tu contraseña"
                    required
                  />
                </Form.Group>

                <div className="d-grid">
                  <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    disabled={loading}
                    className="btn-pichincha"
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Iniciando...
                      </>
                    ) : (
                      'Iniciar Sesión'
                    )}
                  </Button>
                </div>
              </Form>
            </Card.Body>
            <Card.Footer className="text-center bg-light">
              <small className="text-muted">
                ¿No tienes cuenta? <a href="/register" className="text-decoration-none">Regístrate aquí</a>
              </small>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default Login;
