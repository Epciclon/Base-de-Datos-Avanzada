import React, { useState, useEffect } from 'react';
import { Container, Card, Table, Badge, Spinner, Alert } from 'react-bootstrap';
import { transaccionService } from '../services/api';

function TransactionHistory({ user }) {
  const [transacciones, setTransacciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTransacciones();
  }, []);

  const loadTransacciones = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await transaccionService.listarPorCliente();
      setTransacciones(response.data);
    } catch (error) {
      console.error('Error loading transactions:', error);
      let errorMessage = 'Error al cargar las transacciones';
      
      if (error.response) {
        const status = error.response.status;
        switch (status) {
          case 401:
            errorMessage = 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.';
            break;
          case 404:
            errorMessage = 'No se encontraron transacciones para tu cuenta.';
            break;
          case 500:
            errorMessage = 'Error interno del servidor. Intenta nuevamente más tarde.';
            break;
          default:
            errorMessage = 'Error del servidor al cargar transacciones.';
        }
      } else if (error.request) {
        errorMessage = 'No se pudo conectar con el servidor.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const formatearFecha = (fecha) => {
    return new Date(fecha).toLocaleString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTipoTransaccionBadge = (tipo) => {
    const tipos = {
      'RETIRO_CON_TARJETA': { bg: 'danger', text: 'Retiro con Tarjeta' },
      'RETIRO_SIN_TARJETA': { bg: 'warning', text: 'Retiro sin Tarjeta' },
      'DEPOSITO': { bg: 'success', text: 'Depósito' },
      'TRANSFERENCIA': { bg: 'info', text: 'Transferencia' }
    };
    
    const config = tipos[tipo] || { bg: 'secondary', text: tipo };
    return <Badge bg={config.bg}>{config.text}</Badge>;
  };

  if (loading) {
    return (
      <Container className="py-4">
        <div className="text-center">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Cargando historial de transacciones...</p>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-4">
        <Alert variant="danger">
          <Alert.Heading>Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <Card>
        <Card.Header>
          <h4 className="mb-0 text-pichincha-blue">
            <i className="bi bi-clock-history me-2"></i>
            Historial de Transacciones
          </h4>
        </Card.Header>
        <Card.Body>
          {transacciones.length === 0 ? (
            <div className="text-center py-5">
              <i className="bi bi-journal-x text-muted" style={{fontSize: '4rem'}}></i>
              <h5 className="mt-3 text-muted">No hay transacciones registradas</h5>
              <p className="text-muted">
                Tus transacciones aparecerán aquí una vez que realices operaciones
              </p>
            </div>
          ) : (
            <Table responsive striped hover>
              <thead className="table-dark">
                <tr>
                  <th>Fecha</th>
                  <th>Tipo</th>
                  <th>Monto</th>
                  <th>Cuenta</th>
                  <th>Cajero</th>
                  <th>Tarjeta</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {transacciones.map(transaccion => (
                  <tr key={transaccion.ret_id}>
                    <td>{formatearFecha(transaccion.ret_fecha)}</td>
                    <td>{getTipoTransaccionBadge(transaccion.ret_tipo || 'RETIRO_CON_TARJETA')}</td>
                    <td className="fw-bold text-danger">
                      -${parseFloat(transaccion.ret_monto).toFixed(2)}
                    </td>
                    <td className="font-monospace">
                      {transaccion.cuenta?.cuen_numero_cuenta || 'N/A'}
                    </td>
                    <td>
                      <small className="text-muted">
                        {transaccion.cajero?.caj_ubicacion || 'N/A'}
                      </small>
                    </td>
                    <td className="font-monospace">
                      {transaccion.tar_numero_tarjeta ? 
                        `****${transaccion.tar_numero_tarjeta.slice(-4)}` : 
                        'Sin tarjeta'
                      }
                    </td>
                    <td>
                      <Badge bg="success">Completada</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
}

export default TransactionHistory;
