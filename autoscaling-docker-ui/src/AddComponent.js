import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';
import { useState } from 'react';

const AddComponent = () => {
  const [imageName, setImageName] = useState("");
  const [containerName, setContainerName] = useState("");
  const [portNumber, setPortNumber] = useState("");

  const [upAlertName, setUpAlertName] = useState("");
  const [upAlertCond, setUpAlertCond] = useState("");
  const [upAlertAction, setUpAlertAction] = useState("");

  const [downAlertName, setDownAlertName] = useState("");
  const [downAlertCond, setDownAlertCond] = useState("");
  const [downAlertAction, setDownAlertAction] = useState("");

  const [loading, setLoading] = useState(false);

  const postComponent = async () => {
    setLoading(true);
    await fetch("http://localhost:8000/api/v1.0/components/", {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image_name: imageName,
        container_name: containerName,
        port_number: parseInt(portNumber)
      })
    })

    await fetch("http://localhost:5000/add-target", {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "target": containerName
      })
    });

    await fetch("http://localhost:5000/add-rule", {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "target": containerName,
        "name": `${upAlertName}`,
        "expr": upAlertCond
      })
    });

    await fetch("http://localhost:5000/add-rule", {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "target": containerName,
        "name": `${downAlertName}`,
        "expr": downAlertCond
      })
    });

    await fetch("http://localhost:5000/reload", {
      method: 'POST',
      mode: 'cors'
    });

    const data = await fetch("http://localhost:8181/v1/data/scaling/alerts");

    const oldRules = await data.json()

    oldRules.result[`${upAlertName}_${containerName}`] = upAlertAction;
    oldRules.result[`${downAlertName}_${containerName}`] = downAlertAction;

    console.log(oldRules.result);

    await fetch("http://localhost:8181/v1/data/scaling/alerts", {
      method: 'PUT',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(oldRules.result)
    });

    setLoading(false);
    alert("Added.");
  }

  return (
    <Container>
      <Row>
        <h1>Add a new component</h1>
      </Row>
      <Row>
        <Col md="4">
          <h2>Component fields</h2>
          <Form.Group controlId="formImage">
            <Form.Label>Image name</Form.Label>
            <Form.Control type="text" placeholder="aaa/bbbb or bbbb" onChange={e => setImageName(e.target.value)} />
            <Form.Text className="text-muted">
              The image after which the container will be created
            </Form.Text>
          </Form.Group>
          <Form.Group controlId="formContainerName">
            <Form.Label>Container name</Form.Label>
            <Form.Control type="text" placeholder="a-name-with-hyphens" onChange={e => setContainerName(e.target.value)} />
            <Form.Text className="text-muted">
              The name for the container in the system
            </Form.Text>
          </Form.Group>
          <Form.Group controlId="formContainerName">
            <Form.Label>Port number</Form.Label>
            <Form.Control type="number" min="1024" max="65535" placeholder="XXXX" onChange={e => setPortNumber(e.target.value)} />
            <Form.Text className="text-muted">
              The container port to forward
            </Form.Text>
          </Form.Group>
        </Col>
        <Col md="4">
          <h2>Upscaling</h2>
          <Form.Group controlId="formNewAlert">
            <Form.Label>Alert Name</Form.Label>
            <Form.Control type="text" onChange={e => setUpAlertName(e.target.value)} />
            <Form.Text className="text-muted">
              The name for the alert
            </Form.Text>
          </Form.Group>
          <Form.Group controlId="formNewAlert">
            <Form.Label>Condition</Form.Label>
            <Form.Control type="textarea" onChange={e => setUpAlertCond(e.target.value)} />
            <Form.Text className="text-muted">
              The condition (Prometheus) that will trigger the alert<br />
              e.g. {'sum(rate(nginx_vts_upstream_requests_total{job="nginx_vts_exporter-%s"}[5m])) by (backend) > 0.1'}
            </Form.Text>
          </Form.Group>
          <Form.Group controlId="formNewAlert">
            <Form.Label>Action</Form.Label>
            <Form.Control type="textarea" onChange={e => setUpAlertAction(e.target.value)} />
            <Form.Text className="text-muted">
              The action (OPA) to take when the alert fires
            </Form.Text>
          </Form.Group>
        </Col>
        <Col md="4">
          <h2>Downscaling</h2>
          <Form.Group controlId="formNewAlert">
            <Form.Label>Alert Name</Form.Label>
            <Form.Control type="text" onChange={e => setDownAlertName(e.target.value)} />
            <Form.Text className="text-muted">
              The name for the alert
            </Form.Text>
          </Form.Group>
          <Form.Group controlId="formNewAlert">
            <Form.Label>Condition</Form.Label>
            <Form.Control type="textarea" onChange={e => setDownAlertCond(e.target.value)} />
            <Form.Text className="text-muted">
              The condition (Prometheus) that will trigger the alert
            </Form.Text>
          </Form.Group>
          <Form.Group controlId="formNewAlert">
            <Form.Label>Action</Form.Label>
            <Form.Control type="textarea" onChange={e => setDownAlertAction(e.target.value)} />
            <Form.Text className="text-muted">
              The action (OPA) to take when the alert fires
            </Form.Text>
          </Form.Group>
        </Col>
      </Row>
      <Row>
        &nbsp;
      </Row>
      <Row>
        <Col md="4" />
        <Col className="d-grid gap-2">
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
              <Button size="lg" onClick={postComponent}>Add</Button>
          }
        </Col>
        <Col md="4" />
      </Row>
    </Container>
  )
}

export default AddComponent;