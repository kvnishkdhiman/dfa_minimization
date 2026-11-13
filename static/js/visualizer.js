/**
 * DFA-Min Cytoscape.js Graph Visualizer Module.
 * Renders interactive state diagrams for Original and Minimized DFAs.
 */

// Distinct color palette for partition equivalence classes
const PARTITION_COLORS = [
  "#3b82f6", // Blue
  "#10b981", // Emerald
  "#a855f7", // Purple
  "#f59e0b", // Amber
  "#06b6d4", // Cyan
  "#ec4899", // Pink
  "#84cc16", // Lime
  "#f43f5e", // Rose
];

class DFAVisualizer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.cy = null;
    this.initCytoscape();
  }

  initCytoscape() {
    if (!this.container || typeof cytoscape === "undefined") {
      console.warn("Cytoscape container or library not ready:", this.container);
      return;
    }

    this.cy = cytoscape({
      container: this.container,
      boxSelectionEnabled: false,
      autounselectify: false,
      style: [
        // Default State Node
        {
          selector: "node",
          style: {
            "content": "data(label)",
            "text-valign": "center",
            "text-halign": "center",
            "font-family": "'Fira Code', 'Cascadia Code', monospace",
            "font-size": "13px",
            "font-weight": "bold",
            "color": "#ffffff",
            "background-color": "#1e293b",
            "border-width": 2.5,
            "border-color": "#38bdf8",
            "width": 52,
            "height": 52,
            "transition-property": "background-color, border-color, border-width, transform",
            "transition-duration": "0.3s",
          },
        },
        // Initial State (Purple accent)
        {
          selector: "node[?is_initial]",
          style: {
            "border-color": "#a855f7",
            "border-width": 3.5,
          },
        },
        // Accepting State (Double Circle border)
        {
          selector: "node[?is_accepting]",
          style: {
            "border-style": "double",
            "border-width": 7,
            "border-color": "#10b981",
          },
        },
        // Both Initial and Accepting
        {
          selector: "node[?is_initial][?is_accepting]",
          style: {
            "border-color": "#10b981",
            "background-blacken": -0.2,
          },
        },
        // Unreachable State (Dimmed & Red warning)
        {
          selector: "node[?is_unreachable]",
          style: {
            "border-color": "#ef4444",
            "border-style": "dashed",
            "opacity": 0.45,
          },
        },
        // Highlighted Active State (during simulation)
        {
          selector: "node.active-highlight",
          style: {
            "background-color": "#f59e0b",
            "border-color": "#fef08a",
            "border-width": 4,
            "color": "#000000",
            "z-index": 999,
          },
        },
        // Transitions (Directed Edges)
        {
          selector: "edge",
          style: {
            "content": "data(label)",
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#94a3b8",
            "line-color": "#64748b",
            "width": 2,
            "arrow-scale": 1.2,
            "font-family": "'Fira Code', monospace",
            "font-size": "11px",
            "font-weight": "bold",
            "color": "#38bdf8",
            "text-background-opacity": 0.9,
            "text-background-color": "#0f172a",
            "text-background-padding": "3px",
            "text-background-shape": "roundrectangle",
            "text-rotation": "autorotate",
            "loop-direction": "-45deg",
            "loop-sweep": "-90deg",
            "control-point-step-size": 40,
          },
        },
        // Highlighted Edge
        {
          selector: "edge.active-edge",
          style: {
            "line-color": "#f59e0b",
            "target-arrow-color": "#f59e0b",
            "width": 3.5,
            "color": "#fbbf24",
            "z-index": 998,
          },
        },
      ],
      layout: {
        name: "circle",
        padding: 50,
      },
    });
  }

  loadElements(elements, partitionMap = null) {
    if (!this.cy) this.initCytoscape();
    if (!this.cy) return;

    this.cy.elements().remove();
    this.cy.add(elements);

    // Apply partition block colors if supplied
    if (partitionMap) {
      this.cy.nodes().forEach((node) => {
        const stateId = node.id();
        if (partitionMap[stateId] !== undefined) {
          const colorIdx = partitionMap[stateId] % PARTITION_COLORS.length;
          const color = PARTITION_COLORS[colorIdx];
          node.style({
            "background-color": color,
            "border-color": "#ffffff",
          });
        }
      });
    }

    this.applyLayout("circle");
  }

  applyLayout(layoutName = "circle") {
    if (!this.cy) return;

    let layoutOptions = {
      name: layoutName,
      animate: true,
      animationDuration: 400,
      padding: 50,
    };

    if (layoutName === "breadthfirst") {
      layoutOptions.directed = true;
      layoutOptions.roots = this.cy.nodes("[?is_initial]");
      layoutOptions.spacingFactor = 1.3;
    } else if (layoutName === "cose") {
      layoutOptions.idealEdgeLength = 100;
      layoutOptions.nodeOverlap = 20;
      layoutOptions.refresh = 20;
      layoutOptions.fit = true;
    }

    const layout = this.cy.layout(layoutOptions);
    layout.run();
  }

  fit() {
    if (this.cy) this.cy.fit(undefined, 40);
  }

  zoomIn() {
    if (this.cy) this.cy.zoom(this.cy.zoom() * 1.25);
  }

  zoomOut() {
    if (this.cy) this.cy.zoom(this.cy.zoom() * 0.8);
  }

  resetHighlights() {
    if (!this.cy) return;
    this.cy.nodes().removeClass("active-highlight");
    this.cy.edges().removeClass("active-edge");
  }

  highlightState(stateId) {
    if (!this.cy) return;
    this.resetHighlights();
    const node = this.cy.getElementById(stateId);
    if (node) node.addClass("active-highlight");
  }

  async animatePath(path, delayMs = 600) {
    if (!this.cy || !path || path.length === 0) return;

    for (let i = 0; i < path.length; i++) {
      const stateId = path[i];
      this.resetHighlights();
      const node = this.cy.getElementById(stateId);
      if (node) {
        node.addClass("active-highlight");
      }

      if (i > 0) {
        const prevId = path[i - 1];
        const edge = this.cy.edges(`[source = "${prevId}"][target = "${stateId}"]`);
        if (edge) edge.addClass("active-edge");
      }

      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
}
