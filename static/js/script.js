// ==========================================================
// DEVGUARD - GITHUB REPOSITORY HEALTH ANALYZER
// ==========================================================


// ==========================================================
// DOM ELEMENTS
// ==========================================================

const form = document.getElementById(
    "repository-form"
);

const urlInput = document.getElementById(
    "repository-url"
);

const button = document.getElementById(
    "analyze-button"
);

const message = document.getElementById(
    "message"
);

const result = document.getElementById(
    "repository-result"
);


// ==========================================================
// FORM SUBMIT
// ==========================================================

form.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        // --------------------------------------------------
        // Get repository URL
        // --------------------------------------------------

        const repoUrl =
            urlInput.value.trim();


        // --------------------------------------------------
        // Validate URL
        // --------------------------------------------------

        if (!repoUrl) {

            message.textContent =
                "Please enter a GitHub repository URL.";

            message.style.display =
                "block";

            return;
        }


        // --------------------------------------------------
        // Loading state
        // --------------------------------------------------

        message.textContent =
            "Analyzing repository...";

        message.style.display =
            "block";


        result.style.display =
            "none";


        button.disabled =
            true;


        button.textContent =
            "Analyzing...";


        try {

            // ==================================================
            // SEND REQUEST TO FLASK API
            // ==================================================

            const response =
                await fetch(
                    "/api/analyze",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            repository_url:
                                repoUrl
                        })
                    }
                );


            // ==================================================
            // READ API RESPONSE
            // ==================================================

            const data =
                await response.json();


            // ==================================================
            // HANDLE API ERROR
            // ==================================================

            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.error ||
                    "Unable to analyze repository."
                );

            }


            // ==================================================
            // REPOSITORY INFORMATION
            // ==================================================

            const repository =
                data.repository;


            document.getElementById(
                "repo-name"
            ).textContent =
                repository.full_name ||
                repository.name ||
                "Unknown Repository";


            document.getElementById(
                "repo-description"
            ).textContent =
                repository.description ||
                "No description available.";


            document.getElementById(
                "repo-stars"
            ).textContent =
                repository.stars ?? 0;


            document.getElementById(
                "repo-forks"
            ).textContent =
                repository.forks ?? 0;


            document.getElementById(
                "repo-issues"
            ).textContent =
                repository.open_issues ?? 0;


            document.getElementById(
                "repo-language"
            ).textContent =
                repository.language ||
                "Unknown";


            document.getElementById(
                "repo-owner"
            ).textContent =
                repository.owner ||
                "Unknown";


            document.getElementById(
                "repo-branch"
            ).textContent =
                repository.default_branch ||
                "Unknown";


            document.getElementById(
                "repo-license"
            ).textContent =
                repository.license ||
                "No license";


            document.getElementById(
                "repo-visibility"
            ).textContent =
                repository.visibility ||
                "Unknown";


            document.getElementById(
                "repo-size"
            ).textContent =
                repository.size_kb ?? 0;


            document.getElementById(
                "repo-archived"
            ).textContent =
                repository.archived
                    ? "Yes"
                    : "No";


            // --------------------------------------------------
            // GitHub Repository Link
            // --------------------------------------------------

            const githubLink =
                document.getElementById(
                    "github-link"
                );


            githubLink.href =
                repository.html_url ||
                "#";


            // ==================================================
            // REPOSITORY SCAN
            // ==================================================

            const scan =
                data.scan;


            document.getElementById(
                "scan-files"
            ).textContent =
                scan.total_files ?? 0;


            document.getElementById(
                "scan-directories"
            ).textContent =
                scan.total_directories ?? 0;


            document.getElementById(
                "scan-tests"
            ).textContent =
                scan.test_file_count ?? 0;


            document.getElementById(
                "scan-important"
            ).textContent =
                scan.important_file_count ?? 0;


            // ==================================================
            // LANGUAGE COUNTS
            // ==================================================

            const languages =
                scan.language_counts || {};


            document.getElementById(
                "scan-python"
            ).textContent =
                languages.Python ?? 0;


            document.getElementById(
                "scan-javascript"
            ).textContent =
                languages.JavaScript ?? 0;


            document.getElementById(
                "scan-html"
            ).textContent =
                languages.HTML ?? 0;


            document.getElementById(
                "scan-css"
            ).textContent =
                languages.CSS ?? 0;


            // ==================================================
            // CODE QUALITY
            // ==================================================

            const quality =
                data.quality;


            // --------------------------------------------------
            // Quality Score
            // --------------------------------------------------

            document.getElementById(
                "quality-score"
            ).textContent =
                quality.quality_score ?? 0;


            // --------------------------------------------------
            // Files Analyzed
            // --------------------------------------------------

            document.getElementById(
                "quality-files"
            ).textContent =
                quality.files_analyzed ?? 0;


            // --------------------------------------------------
            // Total Lines
            // --------------------------------------------------

            document.getElementById(
                "quality-lines"
            ).textContent =
                quality.total_lines ?? 0;


            // --------------------------------------------------
            // Total Functions
            // --------------------------------------------------

            document.getElementById(
                "quality-functions"
            ).textContent =
                quality.total_functions ?? 0;


            // --------------------------------------------------
            // Long Lines
            // --------------------------------------------------

            document.getElementById(
                "quality-long-lines"
            ).textContent =
                quality.long_line_count ?? 0;


            // --------------------------------------------------
            // Long Functions
            // --------------------------------------------------

            const longFunctions =
                quality.long_functions || [];


            document.getElementById(
                "quality-long-functions"
            ).textContent =
                longFunctions.length;


            // --------------------------------------------------
            // Syntax Errors
            // --------------------------------------------------

            document.getElementById(
                "quality-syntax-errors"
            ).textContent =
                quality.syntax_error_count ?? 0;


            // ==================================================
            // LONG FUNCTIONS LIST
            // ==================================================

            const longFunctionsSection =
                document.getElementById(
                    "long-functions-section"
                );


            const longFunctionsList =
                document.getElementById(
                    "long-functions-list"
                );


            // Clear previous results

            longFunctionsList.innerHTML =
                "";


            if (
                longFunctions.length > 0
            ) {

                longFunctionsSection.style.display =
                    "block";


                longFunctions.forEach(
                    function (item) {

                        const p =
                            document.createElement(
                                "p"
                            );


                        p.textContent =
                            `${item.file} → ` +
                            `${item.name}() ` +
                            `(${item.line_count} lines, ` +
                            `lines ${item.start_line}-` +
                            `${item.end_line})`;


                        longFunctionsList.appendChild(
                            p
                        );

                    }
                );

            }

            else {

                longFunctionsSection.style.display =
                    "none";

            }


            // ==================================================
            // SYNTAX ERRORS LIST
            // ==================================================

            const syntaxErrors =
                quality.syntax_errors || [];


            const syntaxErrorsSection =
                document.getElementById(
                    "syntax-errors-section"
                );


            const syntaxErrorsList =
                document.getElementById(
                    "syntax-errors-list"
                );


            // Clear previous results

            syntaxErrorsList.innerHTML =
                "";


            if (
                syntaxErrors.length > 0
            ) {

                syntaxErrorsSection.style.display =
                    "block";


                syntaxErrors.forEach(
                    function (item) {

                        const p =
                            document.createElement(
                                "p"
                            );


                        p.textContent =
                            `${item.file}: ` +
                            `${item.error}`;


                        syntaxErrorsList.appendChild(
                            p
                        );

                    }
                );

            }

            else {

                syntaxErrorsSection.style.display =
                    "none";

            }


            // ==================================================
            // SHOW RESULTS
            // ==================================================

            result.style.display =
                "block";


            message.textContent =
                "Repository analyzed successfully.";


        }


        // ==================================================
        // ERROR HANDLING
        // ==================================================

        catch (error) {

            console.error(
                "DevGuard analysis error:",
                error
            );


            result.style.display =
                "none";


            message.textContent =
                error.message ||
                "Unable to analyze repository.";

        }


        // ==================================================
        // RESET BUTTON
        // ==================================================

        finally {

            button.disabled =
                false;


            button.textContent =
                "Analyze Repository";

        }

    }
);