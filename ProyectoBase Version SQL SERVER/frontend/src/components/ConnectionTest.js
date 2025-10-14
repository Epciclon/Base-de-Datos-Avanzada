import React, { useState, useEffect } from 'react';
import { Alert, Button, Card, Container } from 'react-bootstrap';
import api from '../services/api';

function ConnectionTest() {
  const [status, setStatus] = useState('checking');
  const [message, setMessage] = useState('');
  const [details, setDetails] = useState('');

  const testConnection = async () => {
    setStatus('checking');
    setMessage('Verificando conexión con el servidor...');
    setDetails('');
    
    try {
      // Probar endpoint básico
      const response = await api.get('/health');
      
      if (response.status === 200) {
        setStatus('success');
        setMessage('¡Conexión exitosa con el backend!');
        setDetails(`Servidor: ${JSON.stringify(response.data, null, 2)}`);
      }
    } catch (error) {
      setStatus('error');
      
      if (error.response) {
        // El servidor respondió con un código de error
        setMessage(`Error del servidor: ${error.response.status}`);
        setDetails(`Detalles: ${JSON.stringify(error.response.data, null, 2)}`);
      } else if (error.request) {
        // No se pudo hacer la petición
        setMessage('No se pudo conectar con el servidor');
        setDetails(`¿Está el backend ejecutándose en http://localhost:8000?
        
Error: ${error.message}
        
Verifique que:
1. El backend FastAPI esté ejecutándose
2. El puerto 8000 esté disponible
3. No hay problemas de CORS`);
      } else {
        // Error de configuración
        setMessage('Error de configuración');
        setDetails(error.message);
      }
    }
  };

  useEffect(() => {
    testConnection();
  }, []);

  const getVariant = () => {
    switch (status) {
      case 'success': return 'success';
      case 'error': return 'danger';
      default: return 'info';
    }
  };

  return (
    <Container className="py-4">
      <Card>
        <Card.Header>
          <h5 className="mb-0">
            <i className="bi bi-wifi me-2"></i>
            Test de Conexión - Banco Pichincha API
          </h5>
        </Card.Header>
        <Card.Body>
          <Alert variant={getVariant()}>
            <Alert.Heading>
              {status === 'checking' && <i className="bi bi-arrow-clockwise me-2"></i>}
              {status === 'success' && <i className="bi bi-check-circle me-2"></i>}
              {status === 'error' && <i className="bi bi-exclamation-triangle me-2"></i>}
              Estado: {message}
            </Alert.Heading>
            {details && (
              <div>
                <hr />
                <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.9em' }}>
                  {details}
                </pre>
              </div>
            )}
          </Alert>
          
          <Button 
            variant="primary" 
            onClick={testConnection}
            disabled={status === 'checking'}
          >
            {status === 'checking' ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                Verificando...
              </>
            ) : (
              <>
                <i className="bi bi-arrow-clockwise me-2"></i>
                Probar Conexión
              </>
            )}
          </Button>
          
          <div className="mt-3">
            <small className="text-muted">
              <strong>URL del Backend:</strong> {process.env.REACT_APP_API_URL || 'http://localhost:8000'}
            </small>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
}

export default ConnectionTest;
