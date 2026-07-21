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
            <div className="filter-toolbar">
                <div className="filter-bar" aria-label="Filter projects by technology">
                {techOptions.map((tech) => (
                    <button
                        className={tech === selectedTech ? "filter-button active" : "filter-button"}
                        key={tech}
                        type="button"
                        aria-pressed={tech === selectedTech}
                        onClick={() => setSelectedTech(tech)}
                    >
                        {tech}
                    </button>
                ))}
                </div>
                <p className="filter-result" aria-live="polite">
                    {visibleProjects.length} {visibleProjects.length === 1 ? "project" : "projects"}
                </p>
            </div>

            <div className="project-grid">
                {visibleProjects.map((project) => (
                    <article className="project-card" key={project.title}>
                        {project.image_url && (
                            <a className="project-card-image-link" href={project.detail_url} aria-label={`${project.title} case study`}>
                                <img
                                    className="project-card-image"
                                    src={project.image_url}
                                    alt={`${project.title} screenshot`}
                                    loading="lazy"
                                    decoding="async"
                                />
                            </a>
                        )}

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
