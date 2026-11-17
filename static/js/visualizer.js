/**
 * DFA-Min Cytoscape.js Graph Visualizer Module.
 * Renders interactive state diagrams for Original and Minimized DFAs.
 * Aesthetic: Acme / Financial Luxury Dark Theme with Amber Accents.
 */

// Distinct color palette for partition equivalence classes:
// Block 0: Blue (#2563eb) - always contains initial state
// Block 1: Green (#10b981) - contains accepting states
const PARTITION_COLORS = [
  "#2563eb", // Blue (Block 0, Initial State)
  "#10b981", // Emerald Green (Block 1, Accepting States)
  "#f59e0b", // Amber
  "#8b5cf6", // Purple
  "#ec4899", // Pink
  "#06b6d4", // Cyan
  "#f97316", // Warm Orange
  "#14b8a6", // Teal
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
        // Default State Node (Sleek dark obsidian)
        {
          selector: "node",
          style: {
            "content": "data(label)",
            "text-valign": "center",
            "text-halign": "center",
            "font-family": "'Fira Code', 'Inter', monospace",
            "font-size": "13px",
            "font-weight": "bold",
            "color": "#ffffff",
            "background-color": "#121620",
            "border-width": 2,
            "border-color": "#334155",
            "width": 54,
            "height": 54,
            "transition-property": "background-color, border-color, border-width, transform",
            "transition-duration": "0.3s",
          },
        },
        // Initial State (Blue fill with Cyan bold border)
        {
          selector: "node[?is_initial]",
          style: {
            "background-color": "#1d4ed8",
            "border-color": "#38bdf8",
            "border-width": 3.5,
          },
        },
        // Accepting State (Double Circle Green border with Green fill)
        {
          selector: "node[?is_accepting]",
          style: {
            "background-color": "#064e3b",
            "border-style": "double",
            "border-width": 7,
            "border-color": "#10b981",
          },
        },
        // Both Initial and Accepting
        {
          selector: "node[?is_initial][?is_accepting]",
          style: {
            "background-color": "#1e3a8a",
            "border-style": "double",
            "border-width": 7,
            "border-color": "#10b981",
          },
        },
        // Unreachable State (Dashed Red border & Dimmed Red)
        {
          selector: "node[?is_unreachable]",
          style: {
            "background-color": "#2e080b",
            "border-color": "#ef4444",
            "border-style": "dashed",
            "border-width": 2.5,
            "opacity": 0.65,
          },
        },
        // Highlighted Active State (during simulation)
        {
          selector: "node.active-highlight",
          style: {
            "background-color": "#f97316",
            "border-color": "#fde047",
            "border-width": 4,
            "color": "#ffffff",
            "z-index": 999,
          },
        },
        // Transitions (Directed Edges with Amber/Orange Accents)
        {
          selector: "edge",
          style: {
            "content": "data(label)",
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#f97316",
            "line-color": "#475569",
            "width": 2,
            "arrow-scale": 1.2,
            "font-family": "'Fira Code', monospace",
            "font-size": "11px",
            "font-weight": "bold",
            "color": "#fb923c",
            "text-background-opacity": 0.95,
            "text-background-color": "#090b10",
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
            "line-color": "#f97316",
            "target-arrow-color": "#fbbf24",
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

    this.applyPartitionColors(partitionMap);
    this.applyLayout("circle");
  }

  applyPartitionColors(partitionMap) {
    if (!this.cy) return;
    this.cy.nodes().forEach((node) => {
      const stateId = node.id();
      const isInitial = Boolean(node.data("is_initial"));
      const isAccepting = Boolean(node.data("is_accepting"));
      const isUnreachable = Boolean(node.data("is_unreachable"));

      if (isUnreachable) {
        node.style({
          "background-color": "#2e080b",
          "border-color": "#ef4444",
          "border-style": "dashed",
          "border-width": 2.5,
          "opacity": 0.65,
        });
        return;
      }

      if (partitionMap && partitionMap[stateId] !== undefined) {
        const colorIdx = partitionMap[stateId] % PARTITION_COLORS.length;
        const color = PARTITION_COLORS[colorIdx];
        node.style({
          "background-color": color,
          "border-style": isAccepting ? "double" : "solid",
          "border-width": isAccepting ? 7 : (isInitial ? 3.5 : 2),
          "border-color": isAccepting ? "#10b981" : (isInitial ? "#38bdf8" : "rgba(255, 255, 255, 0.7)"),
        });
      } else {
        // Restore standard styling
        if (isInitial && isAccepting) {
          node.style({
            "background-color": "#1e3a8a",
            "border-style": "double",
            "border-width": 7,
            "border-color": "#10b981",
          });
        } else if (isInitial) {
          node.style({
            "background-color": "#1d4ed8",
            "border-style": "solid",
            "border-width": 3.5,
            "border-color": "#38bdf8",
          });
        } else if (isAccepting) {
          node.style({
            "background-color": "#064e3b",
            "border-style": "double",
            "border-width": 7,
            "border-color": "#10b981",
          });
        } else {
          node.style({
            "background-color": "#121620",
            "border-style": "solid",
            "border-width": 2,
            "border-color": "#334155",
          });
        }
      }
    });
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
