import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import ListGroup from 'react-bootstrap/ListGroup';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import { useState } from 'react';

const DropComponent = () => {
  const [show, setShow] = useState(false);

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);
  return (
    <Container>
      <Row>
        <h1>Click on a component to drop it</h1>
      </Row>
      <Row>
        <Col md="4">
          <ListGroup>
            <ListGroup.Item action variant="danger" onClick={handleShow}>
              DROP Component 1
            </ListGroup.Item>
            <ListGroup.Item />
            <ListGroup.Item action variant="danger" onClick={handleShow}>
              DROP Component 2
            </ListGroup.Item>
            <ListGroup.Item />
            <ListGroup.Item action variant="danger" onClick={handleShow}>
              DROP Component 3
            </ListGroup.Item>
            <ListGroup.Item />
            <ListGroup.Item action variant="danger" onClick={handleShow}>
              DROP Component 4
            </ListGroup.Item>
          </ListGroup>
        </Col>
      </Row>
      <Modal show={show} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>Drop COMPONENT1</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          <p>This will destroy all instances of the component, the proxy and the alert and action rules.</p>
          <p>Are you sure?</p>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>Close</Button>
          <Button variant="danger">Drop</Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default DropComponent;