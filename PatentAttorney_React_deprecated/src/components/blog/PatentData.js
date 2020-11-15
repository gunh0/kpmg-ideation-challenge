import React from "react";
import 'antd/dist/antd.css';

import {
    Card,
    CardHeader,
    CardBody,
    CardFooter,
    Button,
    Row,
    Col
} from "shards-react";

const PatentData = props => {
    return (
        <Card small className="blog-comments">
            <CardHeader className="border-bottom">
                <h6 className="m-0">Patents</h6>
            </CardHeader>
            <CardBody className="p-0">
                {props.data.map((patent, idx) => (
                    <div key={idx} className="blog-comments__item d-flex p-3">
                        <div className="blog-comments__avatar mr-3">
                            <img src={patent.representative_figure_link} alt={patent.representative_figure_link} />
                        </div>

                        {/* Content */}
                        <div className="blog-comments__content">
                            {/* Content :: Title */}
                            <div className="blog-comments__meta text-mutes">
                                <a className="text-secondary" href={patent.result_link}>
                                    {patent.inventor_author}
                                </a>{" "}
                                |{" "}
                                <a className="text-secondary" href={patent.result_link}>
                                    {patent.assignee}
                                </a>
                                <span className="text-mutes"> / Priority : {patent.priority_date}</span>
                            </div>

                            {/* Content :: Body */}
                            <p className="m-0 my-1 mb-2 text-muted">{patent.title}</p>
                            <p className="m-0 my-1 mb-2 text-muted">[Filing/Creation : {patent.filing_creation_date}] [Publication : {patent.publication_date}] [Grant : {patent.grant_date}]</p>
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
};

export default PatentData;
