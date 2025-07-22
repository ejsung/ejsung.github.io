---
title: "Coding Projects"
layout: single
date: 2024-3-20
classes: wide
permalink: /coding_projects/
tags: [coding, software, simulation]
---

<!-- ---
title: "Coding Projects"
layout: single
created_at: 2024-3-20
last_modified_at: 2024-3-30
classes: wide
permalink: /coding_projects/
--- -->

Most of my coding projects are inspired from my research and favorite subjects. I also do projects that stem from eclectic interests such as video games and/or optimizing my life!

Please see my github for full project details: <a href = "https://github.com/ejsung?tab=repositories" target = "_blank">https://github.com/ejsung?tab=repositories</a>

<!-- <p style="text-align: left;">
    <font size="+2">
    <strong>Ising Model Simulation
    <span style="float:right;">
        Fall 2022
    </span>
    </strong>
    </font>
</p>

<p style="text-align: left;">
    <font size="+2">
    <strong>Elastic Collision of Gas Molecules
    <span style="float:right;">
        Fall 2022
    </span>
    </strong>
    </font>
</p>

<p style="text-align: left;">
    <font size="+2">
    <strong>Temperature Converter
    <span style="float:right;">
        Fall 2021
    </span>
    </strong>
    </font>
</p>

<p style="text-align: left;">
    <font size="+2">
    <strong>Numerical Analysis Algorithms
    <span style="float:right;">
        Fall 2020-Fall 2021 (Ongoing)
    </span>
    </strong>
    </font>
</p> -->



<!-- ## Ising Model Simulation

This simulation demonstrates the Ising model using the Metropolis algorithm. The black cells represent spins in one state, and the white cells represent spins in the opposite state.

<canvas id="isingCanvas" width="400" height="400" style="border:1px solid black;"></canvas>

<script>
    const canvas = document.getElementById('isingCanvas');
    const ctx = canvas.getContext('2d');
    const size = 400; // Size of the canvas
    const numCells = 100; // Number of cells along a dimension
    const cellSize = size / numCells;
    const T = 2.0; // Temperature
    const k = 1; // Boltzmann constant, often set to 1 in simulations

    // Initialize spins randomly
    let spins = Array.from({length: numCells}, () => Array.from({length: numCells}, () => Math.random() > 0.5 ? 1 : -1));

    // Draw the initial state
    function draw() {
        for (let i = 0; i < numCells; i++) {
            for (let j = 0; j < numCells; j++) {
                ctx.fillStyle = spins[i][j] === 1 ? 'black' : 'white';
                ctx.fillRect(i * cellSize, j * cellSize, cellSize, cellSize);
            }
        }
    }

    // Calculate the change in energy from flipping a spin
    function deltaEnergy(i, j) {
        const sumNeighbors = (
            spins[(i+1) % numCells][j] + 
            spins[i][(j+1) % numCells] + 
            spins[(i-1 + numCells) % numCells][j] + 
            spins[i][(j-1 + numCells) % numCells]
        );
        return 2 * spins[i][j] * sumNeighbors;
    }

    // Perform one Monte Carlo step
    function monteCarloStep() {
        for (let n = 0; n < numCells * numCells; n++) {
            const i = Math.floor(Math.random() * numCells);
            const j = Math.floor(Math.random() * numCells);
            const dE = deltaEnergy(i, j);

            if (dE <= 0 || Math.random() < Math.exp(-dE / (k * T))) {
                spins[i][j] *= -1; // Flip the spin
            }
        }
        draw();
    }

    // Update the simulation regularly
    setInterval(monteCarloStep, 100);

    draw();
</script> -->