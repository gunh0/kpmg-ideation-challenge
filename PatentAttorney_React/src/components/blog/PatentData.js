import React from "react";
import { List, Avatar, Icon } from "antd";
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

const IconText = ({ type, text }) => (
    <span>
        <Icon
            type={type}
            style={{
                marginRight: 8
            }}
        />
        {text}
    </span>
);

const PatentData = props => {
    return (
        <Card small className="blog-comments">
            <CardHeader className="border-bottom">
                <h6 className="m-0">Patents</h6>
            </CardHeader>
            <CardBody className="p-0">
                <List
                    itemLayout="vertical"
                    size="large"
                    pagination={{
                        onChange: page => {
                            console.log(page);
                        },
                        pageSize: 5
                    }}
                    dataSource={props.data}
                    renderItem={item => (
                        <List.Item
                            key={item.title}
                            actions={[
                                <IconText type="star-o" text="156" />,
                                <IconText type="like-o" text="156" />,
                                <IconText type="message" text="2" />
                            ]}
                            extra={
                                <img
                                    width={200}
                                    alt="logo"
                                    src={item.representative_figure_link}
                                />
                            }
                        >
                            <List.Item.Meta
                                avatar={<Avatar src={item.result_link} />}
                                title={<a href={item.result_link}> {item.title} </a>}
                                description={item.title}
                            />
                            {item.content}
                        </List.Item>
                    )}
                />
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
