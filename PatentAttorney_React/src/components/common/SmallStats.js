import React from "react";
import axios from "axios";
import PropTypes from "prop-types";
import classNames from "classnames";
import { Card } from "shards-react";

import PatentData from "../blog/PatentData"

class SmallStats extends React.Component {
  constructor(props) {
    super(props);

    this.canvasRef = React.createRef();
  }

  state = {
    articles: []
  };

  fetchArticles = () => {
    axios.get("http://127.0.0.1:8000/api/").then(res => {
      this.setState({
        articles: res.data
      });
    });
  }

  componentDidMount() {
    this.fetchArticles();
  }

  componentWillReceiveProps(newProps) {
    if (newProps.token) {
      this.fetchArticles();      
    }
  }

  render() {
    const { variation } = this.props;

    const cardClasses = classNames(
      "stats-small",
      variation && `stats-small--${variation}`
    );

    return (
      <Card small className={cardClasses}>
        <PatentData data={this.state.articles}/>
      </Card>
    );
  }
}

SmallStats.propTypes = {
  /**
   * The Small Stats variation.
   */
  variation: PropTypes.string,
  /**
   * The label.
   */
  label: PropTypes.string,
  /**
   * The value.
   */
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  /**
   * The percentage number or string.
   */
  percentage: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  /**
   * Whether is a value increase, or not.
   */
  increase: PropTypes.bool,
  /**
   * The Chart.js configuration object.
   */
  chartConfig: PropTypes.object,
  /**
   * The Chart.js options object.
   */
  chartOptions: PropTypes.object,
  /**
   * The chart data.
   */
  chartData: PropTypes.array.isRequired,
  /**
   * The chart labels.
   */
  chartLabels: PropTypes.array,
  articles: PropTypes.array
};

SmallStats.defaultProps = {
  increase: true,
  percentage: 0,
  value: 0,
  label: "Label",
  chartOptions: Object.create(null),
  chartConfig: Object.create(null),
  chartData: [],
  chartLabels: [],
  articles: []
};

export default SmallStats;
