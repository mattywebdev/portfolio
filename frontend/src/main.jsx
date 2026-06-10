import React from "react";
import { createRoot } from "react-dom/client";
import ProjectFilter from "./ProjectFilter";

const projectsData = document.getElementById("projects-data");
const projectRoot = document.getElementById("project-filter-root");

if (projectsData && projectRoot) {
    const projects = JSON.parse(projectsData.textContent);

    createRoot(projectRoot).render(
        <React.StrictMode>
            <ProjectFilter projects={projects} />
        </React.StrictMode>,
    );
}