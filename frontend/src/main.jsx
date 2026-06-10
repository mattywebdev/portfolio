import React from "react";
import { createRoot } from "react-dom/client";
import ProjectFilter from "./ProjectFilter";

const projectRoot = document.getElementById("project-filter-root");

if (projectRoot) {
    const projects = JSON.parse(projectRoot.dataset.projects || "[]");

    createRoot(projectRoot).render(
        <React.StrictMode>
            <ProjectFilter projects={projects} />
        </React.StrictMode>,
    );
}