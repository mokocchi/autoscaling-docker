import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Spinner from 'react-bootstrap/Spinner';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import { useState } from 'react';

const DropComponent = () => {
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  const restart = async () => {
    setLoading(true);
    handleClose();
    await fetch("http://localhost:8000/api/v1.0/restart/");
    setLoading(false);
  }
  return (
    <Container>
      <Row>
        <Col>
          <h1>Restart the autoscaler</h1>
          {
            loading ?
              <Button size="lg" variant="secondary">
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                />
              </Button>
              :
              <Button variant="danger" onClick={handleShow}>RESET</Button>
          }
        </Col>
      </Row>
      <Modal show={show} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>RESET</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          <p>This will destroy all instances of the components, the proxy and the alert and action rules, plus Prometheus and OPA.</p>
          <p>Are you sure?</p>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>Close</Button>
          <Button variant="danger" onClick={restart}>Restart</Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default DropComponent;