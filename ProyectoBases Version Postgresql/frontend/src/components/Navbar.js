import React from 'react';
import { Navbar as BootstrapNavbar, Nav, Container, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

function Navbar({ user, onLogout }) {
  return (
    <BootstrapNavbar bg="dark" variant="dark" expand="lg" className="navbar-pichincha">
      <Container>
        <BootstrapNavbar.Brand as={Link} to="/">
          <i className="bi bi-bank2 me-2"></i>
          Banco Pichincha
        </BootstrapNavbar.Brand>
        <BootstrapNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BootstrapNavbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/">Inicio</Nav.Link>
            <Nav.Link as={Link} to="/cajero">Cajero ATM</Nav.Link>
            {!user && (
              <>
                <Nav.Link as={Link} to="/register">Registrarse</Nav.Link>
                <Nav.Link as={Link} to="/login">Iniciar Sesión</Nav.Link>
              </>
            )}
            {user && (
              <>
                <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>
                <Nav.Link as={Link} to="/transactions">Transacciones</Nav.Link>
              </>
            )}
          </Nav>
          {user && (
            <Nav>
              <BootstrapNavbar.Text className="me-3">
                Bienvenido, {user.nombre || user.usuario}
              </BootstrapNavbar.Text>
              <Button variant="outline-light" size="sm" onClick={onLogout}>
                Cerrar Sesión
              </Button>
            </Nav>
          )}
        </BootstrapNavbar.Collapse>
      </Container>
    </BootstrapNavbar>
  );
}

export default Navbar;
