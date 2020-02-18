import React from "react";
import PropTypes from "prop-types";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
  Row,
  Col
} from "shards-react";

const Discussions = ({ title, patents}) => (
  <Card small className="blog-comments">
    <CardHeader className="border-bottom">
      <h6 className="m-0">{title}</h6>
    </CardHeader>
    
    <CardBody className="p-0">
      {patents.map((patent, idx) => (
        <div key={idx} className="blog-comments__item d-flex p-3">
          <div className="blog-comments__avatar mr-3">
            <img src={patent.representative_figure_link} alt={patent.representative_figure_link} />
          </div>
        
          {/* Content */}
          <div className="blog-comments__content">
            {/* Content :: Title */}
            <div className="blog-comments__meta text-mutes">
              <a className="text-secondary" href={patent.result_link}>
                {patent.inventor}
              </a>{" "}
              |{" "}
              <a className="text-secondary" href={patent.result_link}>
                {patent.assignee}
              </a>
              <span className="text-mutes"> / {patent.publication_date}</span>
            </div>

            {/* Content :: Body */}
            <p className="m-0 my-1 mb-2 text-muted">{patent.title}</p>
          </div>
        </div>
      ))}
    </CardBody>

    <CardFooter className="border-top">
      <Row>
        <Col className="text-center view-report">
          <Button theme="white" type="submit">
            View All Comments
          </Button>
        </Col>
      </Row>
    </CardFooter>
  </Card>
);

Discussions.propTypes = {
  title: PropTypes.string,
  patents: PropTypes.array
};

const listData = [];
for (let i = 0; i < 15; i++) {
  listData.push({
    id: "US-7524089-B2",
    title: "LED illuminating device for providing a uniform light spot",
    assignee: "Daejin Dmp Co., Ltd.",
    inventor: "Hitora Shozo, Tokio Kawashima",
    priority_date: "2004-02-06",
    creation_date: "2004-02-06",
    publication_date: "2004-02-06",
    grant_date: "2004-02-06",
    result_link: "https://patents.google.com/patent/US6033087A/en",
    representative_figure_link: "https://patentimages.storage.googleapis.com/pages/US6033087-1.png",
  });
}

Discussions.defaultProps = {
  title: "Patents",
  patents: listData
};

export default Discussions;
