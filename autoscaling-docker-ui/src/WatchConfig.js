import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';
import { useEffect, useState } from 'react';

const WatchConfig = () => {
  const [loading, setLoading] = useState(false);
  const [targets, setTargets] = useState([]);
  const [actions, setActions] = useState({});

  const getRules = async () => {
    setLoading(true);
    const data = await fetch("http://localhost:5000/rules");
    const targets = await data.json();
    setTargets(targets);
    const data2 = await fetch('http://localhost:8181/v1/data/scaling/alerts');
    const actions = await data2.json();
    setActions(actions.result);
    setLoading(false);
  }

  useEffect(() => getRules(), [])

  return (
    <Container>
      <Row>
        <h1>Current configuration</h1>
      </Row>
      <Row>
        <Col md="12">
          {targets.map((tgt, idx) => (<div key={idx}>
            <h2>{tgt.name.split("scaling-nginx-")[1]}</h2>
            {
              tgt.rules.map((rule, idx) => (<div key={`rule-${idx}`}>
                <h3>{rule.alert}</h3>
                <ul>
                  <li> Alert: {rule.expr}</li>
                  <li> Action: {actions[rule.alert]}</li>
                </ul>
                </div>))
            }
          </div>
          ))}
        </Col>
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
              <Button size="lg" onClick={getRules}>Refresh</Button>
          }
        </Col>
        <Col md="4" />
      </Row>
    </Container>
  )
}

export default WatchConfig;