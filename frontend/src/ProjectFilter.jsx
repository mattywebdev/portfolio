import { useMemo, useState } from "react";

export default function ProjectFilter({ projects }) {
    const [selectedTech, setSelectedTech] = useState("All");

    const techOptions = useMemo(() => {
        const tech = projects.flatMap((project) => project.tech);
        return ["All", ...Array.from(new Set(tech)).sort()];
    }, [projects]);

    const visibleProjects = useMemo(() => {
        if (selectedTech === "All") {
            return projects;
        }

        return projects.filter((project) => project.tech.includes(selectedTech));
    }, [projects, selectedTech]);

    return (
        <div className="react-projects">
            <div className="filter-bar" aria-label="Filter projects by technology">
                {techOptions.map((tech) => (
                    <button
                        className={tech === selectedTech ? "filter-button active" : "filter-button"}
                        key={tech}
                        type="button"
                        onClick={() => setSelectedTech(tech)}
                    >
                        {tech}
                    </button>
                ))}
            </div>

            <div className="project-grid">
                {visibleProjects.map((project) => (
                    <article className="project-card" key={project.title}>
                        <div className="project-card-header">
                            <h3>{project.title}</h3>
                            <span>{project.status}</span>
                        </div>
                        <p>{project.description}</p>
                        <ul className="tag-list" aria-label={`Technologies used for ${project.title}`}>
                          {project.tech.map((item) => (
                              <li key={item}>{item}</li>
                          ))}
                      </ul>

                      <div className="project-card-actions">
                          <a className="text-link" href={project.detail_url}>
                              Case study
                          </a>

                          {project.url && (
                              <a className="text-link" href={project.url} target="_blank" rel="noreferrer">
                                  Live site
                              </a>
                          )}

                          {project.source_url && (
                              <a className="text-link" href={project.source_url} target="_blank" rel="noreferrer">
                                  Code
                              </a>
                          )}
                      </div>
                    </article>
                ))}
            </div>
        </div>
    );
}