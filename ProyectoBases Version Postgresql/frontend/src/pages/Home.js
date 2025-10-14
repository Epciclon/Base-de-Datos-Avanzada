import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <>
      {/* Hero Section */}
      <section className="hero-section">
        <Container>
          <Row className="align-items-center">
            <Col lg={6}>
              <h1 className="display-4 fw-bold mb-4">
                Bienvenido al Banco Pichincha
              </h1>
              <p className="lead mb-4">
                Tu banco de confianza para todas tus necesidades financieras. 
                Gestiona tus cuentas, tarjetas y transacciones de manera segura y eficiente.
              </p>
              <div className="d-grid gap-2 d-md-flex">
                <Button as={Link} to="/register" variant="warning" size="lg" className="me-md-2">
                  Registrarse
                </Button>
                <Button as={Link} to="/login" variant="outline-light" size="lg">
                  Iniciar Sesión
                </Button>
              </div>
            </Col>
            <Col lg={6} className="text-center">
              <i className="bi bi-bank2" style={{fontSize: '15rem', opacity: 0.8}}></i>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Features Section */}
      <section className="py-5">
        <Container>
          <Row className="text-center mb-5">
            <Col>
              <h2 className="display-5 fw-bold text-pichincha-blue">Nuestros Servicios</h2>
              <p className="lead text-muted">
                Descubre todo lo que el Banco Pichincha tiene para ofrecerte
              </p>
            </Col>
          </Row>
          <Row className="g-4">
            <Col md={4}>
              <Card className="h-100 border-0 shadow card-hover">
                <Card.Body className="text-center p-4">
                  <div className="mb-3">
                    <i className="bi bi-person-plus-fill text-primary" style={{fontSize: '3rem'}}></i>
                  </div>
                  <Card.Title className="h4 text-pichincha-blue">Gestión de Clientes</Card.Title>
                  <Card.Text className="text-muted">
                    Registro y administración completa de información personal con 
                    los más altos estándares de seguridad.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4}>
              <Card className="h-100 border-0 shadow card-hover">
                <Card.Body className="text-center p-4">
                  <div className="mb-3">
                    <i className="bi bi-credit-card-fill text-primary" style={{fontSize: '3rem'}}></i>
                  </div>
                  <Card.Title className="h4 text-pichincha-blue">Cuentas y Tarjetas</Card.Title>
                  <Card.Text className="text-muted">
                    Manejo integral de cuentas bancarias y tarjetas de débito y crédito 
                    con tecnología de vanguardia.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4}>
              <Card className="h-100 border-0 shadow card-hover">
                <Card.Body className="text-center p-4">
                  <div className="mb-3">
                    <i className="bi bi-arrow-left-right text-primary" style={{fontSize: '3rem'}}></i>
                  </div>
                  <Card.Title className="h4 text-pichincha-blue">Transacciones</Card.Title>
                  <Card.Text className="text-muted">
                    Retiros seguros con y sin tarjeta en cajeros automáticos, 
                    disponibles las 24 horas del día.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Call to Action */}
      <section className="py-5 bg-light">
        <Container>
          <Row className="text-center">
            <Col>
              <h3 className="h2 text-pichincha-blue mb-4">¿Listo para comenzar?</h3>
              <p className="lead text-muted mb-4">
                Únete a miles de clientes que confían en el Banco Pichincha
              </p>
              <Button as={Link} to="/register" variant="primary" size="lg" className="btn-pichincha">
                Abrir Cuenta Ahora
              </Button>
              <div className="mt-3">
                <small>
                  <Link to="/test-connection" className="text-muted text-decoration-none">
                    <i className="bi bi-gear me-1"></i>
                    Verificar conexión del sistema
                  </Link>
                </small>
              </div>
            </Col>
          </Row>
        </Container>
      </section>
    </>
  );
}

export default Home;
