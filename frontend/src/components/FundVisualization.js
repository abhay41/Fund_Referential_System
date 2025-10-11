import React, { useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import * as d3 from 'd3';
import { Box, Paper } from '@mui/material';

const FundVisualization = () => {
  const { fundId } = useParams();
  const svgRef = useRef();

  useEffect(() => {
    if (!fundId) return;

    const fetchData = async () => {
      try {
        const response = await fetch(`http://localhost:8000/funds/${fundId}/hierarchy`);
        const data = await response.json();
        renderGraph(data);
      } catch (error) {
        console.error('Error fetching fund data:', error);
      }
    };

    fetchData();
  }, [fundId]);

  const renderGraph = (data) => {
    const width = 800;
    const height = 600;

    // Clear existing visualization
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    // Draw links
    const link = svg.append("g")
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 2);

    // Draw nodes
    const node = svg.append("g")
      .selectAll("circle")
      .data(data.nodes)
      .join("circle")
      .attr("r", 5)
      .attr("fill", d => getNodeColor(d.type))
      .call(drag(simulation));

    // Add labels
    const label = svg.append("g")
      .selectAll("text")
      .data(data.nodes)
      .join("text")
      .text(d => d.name)
      .attr("font-size", 12)
      .attr("dx", 12)
      .attr("dy", 4);

    // Update positions
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
    });
  };

  const getNodeColor = (type) => {
    const colors = {
      Fund: "#1976d2",
      SubFund: "#dc004e",
      ShareClass: "#388e3c",
      ManagementEntity: "#f57c00"
    };
    return colors[type] || "#666";
  };

  const drag = (simulation) => {
    const dragstarted = (event) => {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    };

    const dragged = (event) => {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    };

    const dragended = (event) => {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    };

    return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper elevation={3} sx={{ p: 2 }}>
        <svg ref={svgRef}></svg>
      </Paper>
    </Box>
  );
};

export default FundVisualization;