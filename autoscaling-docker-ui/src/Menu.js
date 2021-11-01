import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Container from 'react-bootstrap/Container';

const Menu =  () => (
  <Navbar bg="light" expand="lg">
  <Container>
    <Navbar.Brand href="/">Autoscaling Docker UI</Navbar.Brand>
    <Navbar.Toggle aria-controls="basic-navbar-nav" />
    <Navbar.Collapse id="basic-navbar-nav">
      <Nav>
          <Nav.Link href="/">Dashboard</Nav.Link>
          <Nav.Link href="/add">AddComponent</Nav.Link>
          <Nav.Link href="/restart">Restart Autoscaler</Nav.Link>
      </Nav>
    </Navbar.Collapse>
  </Container>
</Navbar>
)

export default Menu;