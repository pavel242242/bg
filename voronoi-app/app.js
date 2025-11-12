// Data: Professions and their AI replacement levels
const professions = [
    // High replacement (75-100%)
    { name: "Programmers", replacement: 85, x: 200, y: 150 },
    { name: "Designers", replacement: 80, x: 450, y: 180 },
    { name: "Email Readers", replacement: 90, x: 350, y: 100 },
    { name: "Agile Coaches", replacement: 75, x: 600, y: 220 },

    // Medium-High replacement (50-75%)
    { name: "Movie Makers", replacement: 65, x: 150, y: 350 },
    { name: "Content Writers", replacement: 70, x: 500, y: 380 },
    { name: "Data Analysts", replacement: 68, x: 700, y: 150 },

    // Medium replacement (25-50%)
    { name: "Customer Service Reps", replacement: 45, x: 250, y: 500 },
    { name: "Talkative Grooming Attendees", replacement: 40, x: 550, y: 500 },
    { name: "Social Media Managers", replacement: 48, x: 400, y: 350 },
    { name: "Translators", replacement: 42, x: 750, y: 350 },

    // Low replacement (10-25%)
    { name: "HR Managers", replacement: 20, x: 200, y: 600 },
    { name: "Therapists", replacement: 15, x: 450, y: 650 },
    { name: "Sales Executives", replacement: 22, x: 650, y: 550 },

    // Minimal replacement (0-10%)
    { name: "Plumbers", replacement: 5, x: 100, y: 750 },
    { name: "Electricians", replacement: 6, x: 350, y: 750 },

    // Not yet replaced
    { name: "Lumber Jacks", replacement: 2, x: 550, y: 750 },
    { name: "Teachers", replacement: 3, x: 750, y: 700 },
    { name: "Nurses", replacement: 4, x: 200, y: 850 },
    { name: "Construction Workers", replacement: 3, x: 600, y: 850 }
];

// Color scale based on replacement level
function getColor(replacement) {
    if (replacement >= 75) return "#d73027"; // High - Red
    if (replacement >= 50) return "#fc8d59"; // Medium-High - Orange
    if (replacement >= 25) return "#fee090"; // Medium - Yellow
    if (replacement >= 10) return "#e0f3f8"; // Low - Light Blue
    if (replacement > 5) return "#91bfdb"; // Minimal - Blue
    return "#4575b4"; // Not yet - Dark Blue
}

// Size scale based on replacement level (for visual emphasis)
function getSize(replacement) {
    return Math.sqrt(replacement) * 4 + 20;
}

// Initialize the visualization
const width = 900;
const height = 900;
const margin = { top: 20, right: 20, bottom: 20, left: 20 };

const svg = d3.select("#voronoi")
    .attr("width", width)
    .attr("height", height);

// Create Voronoi layout
const delaunay = d3.Delaunay.from(professions, d => d.x, d => d.y);
const voronoi = delaunay.voronoi([0, 0, width, height]);

// Create tooltip
const tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

// Draw Voronoi cells
const cells = svg.append("g")
    .attr("class", "cells")
    .selectAll("path")
    .data(professions)
    .join("path")
    .attr("d", (d, i) => voronoi.renderCell(i))
    .attr("fill", d => getColor(d.replacement))
    .attr("stroke", "#333")
    .attr("stroke-width", 2)
    .attr("opacity", 0.7)
    .on("mouseover", function(event, d) {
        d3.select(this)
            .attr("opacity", 1)
            .attr("stroke-width", 3);

        tooltip.transition()
            .duration(200)
            .style("opacity", 0.95);

        tooltip.html(`
            <strong>${d.name}</strong><br/>
            <span class="replacement-level">AI Replacement: ${d.replacement}%</span><br/>
            <span class="status">${getStatusText(d.replacement)}</span>
        `)
            .style("left", (event.pageX + 15) + "px")
            .style("top", (event.pageY - 28) + "px");
    })
    .on("mouseout", function(d) {
        d3.select(this)
            .attr("opacity", 0.7)
            .attr("stroke-width", 2);

        tooltip.transition()
            .duration(500)
            .style("opacity", 0);
    });

// Draw profession labels
const labels = svg.append("g")
    .attr("class", "labels")
    .selectAll("text")
    .data(professions)
    .join("text")
    .attr("x", d => d.x)
    .attr("y", d => d.y)
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "middle")
    .attr("fill", d => d.replacement >= 50 ? "#fff" : "#000")
    .attr("font-size", d => Math.max(10, Math.min(14, getSize(d.replacement) / 5)))
    .attr("font-weight", "600")
    .attr("pointer-events", "none")
    .style("text-shadow", d => d.replacement >= 50 ? "1px 1px 2px rgba(0,0,0,0.8)" : "1px 1px 2px rgba(255,255,255,0.8)")
    .each(function(d) {
        const words = d.name.split(" ");
        const text = d3.select(this);

        if (words.length > 1 && d.name.length > 12) {
            text.text("");
            words.forEach((word, i) => {
                text.append("tspan")
                    .attr("x", d.x)
                    .attr("dy", i === 0 ? 0 : "1.1em")
                    .text(word);
            });
        } else {
            text.text(d.name);
        }
    });

// Draw central points (for visual reference)
const points = svg.append("g")
    .attr("class", "points")
    .selectAll("circle")
    .data(professions)
    .join("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", 3)
    .attr("fill", "#000")
    .attr("opacity", 0.3)
    .attr("pointer-events", "none");

// Helper function to get status text
function getStatusText(replacement) {
    if (replacement >= 75) return "⚠️ High risk of automation";
    if (replacement >= 50) return "⚡ Significant automation ongoing";
    if (replacement >= 25) return "📊 Moderate automation";
    if (replacement >= 10) return "🔵 Limited automation";
    if (replacement > 5) return "✓ Minimal automation";
    return "✅ Human-centric profession";
}

// Add animation on load
cells.attr("opacity", 0)
    .transition()
    .duration(1000)
    .delay((d, i) => i * 50)
    .attr("opacity", 0.7);

labels.attr("opacity", 0)
    .transition()
    .duration(1000)
    .delay((d, i) => i * 50 + 500)
    .attr("opacity", 1);

console.log("Voronoi AI Replacement Infographic loaded successfully!");
console.log(`Tracking ${professions.length} professions`);
