

# mkdir -p ~/.zsh/functions
# nano ~/.zsh/functions/dev.zsh

# nano ~/.zshrc

# IN ~/.zshrc import ---->. source ~/.zsh/functions/dev.zsh
# source ~/.zshrc

dev() {
    case "$1" in

        clone)
            if [ -z "$2" ] || [ -z "$3" ]; then
                echo ""
                echo "Usage:"
                echo "  dev clone <username> <repository>"
                echo "  dev clone <username> <repository> <python-version>"
                echo ""
                echo "Examples:"
                echo "  dev clone octocat hello-world"
                echo "  dev clone octocat hello-world 3.12"
                echo "  dev clone octocat hello-world 3.13"
                echo ""
                return 1
            fi

            username="$2"
            repository="$3"
            requested_python="$4"

            clone_url="https://github.com/$username/$repository.git"

            echo ""
            echo "Cloning GitHub repository..."
            echo "Repository: $username/$repository"
            echo ""

            if ! command -v git >/dev/null 2>&1; then
                echo "Error: Git is not installed or not available in PATH."
                return 1
            fi

            if [ -d "$repository" ]; then
                echo "Error: Directory '$repository' already exists."
                echo "Please choose a different directory or remove the existing one."
                return 1
            fi

            git clone "$clone_url"

            if [ $? -ne 0 ]; then
                echo ""
                echo "Error: Failed to clone repository."
                echo "Check the GitHub username, repository name and your network connection."
                return 1
            fi

            cd "$repository" || return 1

            echo ""
            echo "Repository cloned successfully."
            echo "Location: $PWD"
            echo ""

            # =========================================
            # PYTHON VERSION
            # =========================================

            python_cmd=""

            if [ -n "$requested_python" ]; then

                if [[ "$requested_python" != 3.* ]]; then
                    echo "Error: Invalid Python version '$requested_python'."
                    echo "Please use a Python 3 version, for example: 3.12"
                    return 1
                fi

                requested_python_cmd="python${requested_python}"

                if command -v "$requested_python_cmd" >/dev/null 2>&1; then
                    python_cmd="$(command -v "$requested_python_cmd")"
                else
                    echo "Error: Python $requested_python is not installed."
                    echo ""
                    echo "Available Python versions:"
                    echo ""

                    found_python=false

                    for version in 15 14 13 12 11 10 9 8 7 6 5 4; do
                        if command -v "python3.$version" >/dev/null 2>&1; then
                            echo "  Python 3.$version"
                            found_python=true
                        fi
                    done

                    if [ "$found_python" = false ]; then
                        echo "  No Python 3 installation found."
                    fi

                    echo ""
                    return 1
                fi

            else

                # Automatically find the highest installed Python 3 version.
                for version in 15 14 13 12 11 10 9 8 7 6 5 4; do
                    if command -v "python3.$version" >/dev/null 2>&1; then
                        python_cmd="$(command -v "python3.$version")"
                        break
                    fi
                done

                # Fallback to python3 if no specific version was found.
                if [ -z "$python_cmd" ] && command -v python3 >/dev/null 2>&1; then
                    python_cmd="$(command -v python3)"
                fi

            fi

            if [ -z "$python_cmd" ]; then
                echo "Error: No Python 3 installation found."
                echo ""
                echo "Please install Python 3 before using dev clone."
                return 1
            fi

            echo "Using Python:"
            "$python_cmd" --version
            echo ""



            # =========================================
            # VIRTUAL ENVIRONMENT
            # =========================================

            if [ -d ".venv" ]; then
                echo "Error: A .venv directory already exists."
                echo "The repository appears to already contain a virtual environment."
                return 1
            fi

            echo "Creating virtual environment..."
            echo ""

            "$python_cmd" -m venv .venv

            if [ $? -ne 0 ]; then
                echo ""
                echo "Error: Failed to create the virtual environment."
                return 1
            fi

            echo "Virtual environment created."
            echo ""



            # =========================================
            # ACTIVATE VIRTUAL ENVIRONMENT
            # =========================================

            source .venv/bin/activate

            if [ $? -ne 0 ]; then
                echo ""
                echo "Error: Failed to activate the virtual environment."
                return 1
            fi

            echo "Virtual environment activated."
            echo ""



            # =========================================
            # UPDATE PIP
            # =========================================

            echo "Updating pip..."
            echo ""

            python -m pip install --upgrade pip

            if [ $? -ne 0 ]; then
                echo ""
                echo "Warning: pip could not be upgraded."
                echo "Continuing with the existing pip version."
                echo ""
            fi



            # =========================================
            # REQUIREMENTS
            # =========================================

            if [ -f "requirements.txt" ]; then

                echo "requirements.txt found."
                echo "Installing dependencies..."
                echo ""

                python -m pip install -r requirements.txt

                if [ $? -ne 0 ]; then
                    echo ""
                    echo "Error: Failed to install dependencies."
                    echo "The virtual environment is still active."
                    return 1
                fi

                echo ""
                echo "Dependencies installed successfully."

            else

                echo "No requirements.txt found."
                echo "Skipping dependency installation."

            fi



            # =========================================
            # FINISHED
            # =========================================

            echo ""
            echo "────────────────────────────────"
            echo "Dev clone completed successfully."
            echo "────────────────────────────────"
            echo ""
            echo "Repository:"
            echo "  $PWD"
            echo ""
            echo "Python:"
            "$python_cmd" --version
            echo ""
            echo "Virtual environment:"
            echo "  .venv"
            echo ""

            if [ -f "requirements.txt" ]; then
                echo "Dependencies:"
                echo "  Installed from requirements.txt"
                echo ""
            fi

            echo "The virtual environment is currently active."
            echo ""
            ;;






        backup)
            name="${2:-$(basename "$PWD")}"
            timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
            backup_file="${name}_backup_${timestamp}.tar.gz"

            echo "Creating backup: $backup_file"

            tar \
                --exclude=".git" \
                --exclude=".venv" \
                --exclude="venv" \
                --exclude="__pycache__" \
                --exclude="*.pyc" \
                --exclude="node_modules" \
                --exclude="*.tar.gz" \
                -czf "../$backup_file" .

            echo "Backup created: ../$backup_file"
            ;;

        serve)
            port="${2:-8000}"

            if ! [[ "$port" =~ ^[0-9]+$ ]] || [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
                echo "Error: Invalid port."
                echo "Usage: dev serve [port]"
                return 1
            fi

            echo "Starting server on http://localhost:$port"
            echo "Press Ctrl+C to stop."

            python3 -m http.server "$port"
            ;;


        newpy)
            if [ -z "$2" ]; then
                echo "Usage: dev newpy <project-name>"
                return 1
            fi

            mkdir -p "$2"
            cd "$2"
            python3 -m venv venv
            source venv/bin/activate
            echo "Created Python project: $2"
            ;;

        venv)
            if [ -d ".venv" ]; then
                source .venv/bin/activate
            elif [ -d "venv" ]; then
                source venv/bin/activate
            else
                echo "No virtual environment found."
                return 1
            fi
            ;;

        mkcd)
            if [ -z "$2" ]; then
                echo "Usage: dev mkcd <directory>"
                return 1
            fi

            mkdir -p "$2" && cd "$2"
            ;;

        push)
            files=()
            folders=()
            message=""

            while [ "$#" -gt 1 ]; do
                shift

                case "$1" in
                    -f)
                        shift
                        while [ "$#" -gt 1 ] && [ "$1" != "-d" ] && [ "$1" != "-f" ]; do
                            files+=("$1")
                            shift
                        done
                        ;;

                    -d)
                        shift
                        while [ "$#" -gt 1 ] && [ "$1" != "-d" ] && [ "$1" != "-f" ]; do
                            folders+=("$1")
                            shift
                        done
                        ;;

                    *)
                        message="$*"
                        break
                        ;;
                esac
            done

            if [ -z "$message" ]; then
                echo "Error: No commit message provided."
                return 1
            fi

            if [ ${#files[@]} -eq 0 ] && [ ${#folders[@]} -eq 0 ]; then
                echo "Adding all changes..."
                git add .
            else
                if [ ${#files[@]} -gt 0 ]; then
                    echo "Adding files: ${files[*]}"
                    git add -- "${files[@]}"
                fi

                if [ ${#folders[@]} -gt 0 ]; then
                    echo "Adding folders: ${folders[*]}"
                    git add -- "${folders[@]}"
                fi
            fi

            echo "Creating commit: $message"
            git commit -m "$message"

            echo "Pushing changes..."
            git push

            echo "Done!"
            ;;


        "")
            echo ""
            echo "Dev CLI"
            echo "────────────────────────────────"
            echo ""
            echo "Available commands:"
            echo ""
            echo "  dev newpy <name>"
            echo "      Create a new Python project"
            echo ""
            echo "  dev venv"
            echo "      Activate the virtual environment"
            echo ""
            echo "  dev mkcd <directory>"
            echo "      Create a directory and enter it"
            echo ""
            echo "  dev push <message>"
            echo "      Add, commit and push all changes"
            echo ""
            echo "  dev push -f <files> <message>"
            echo "      Push selected files"
            echo ""
            echo "  dev push -d <folder> <message>"
            echo "      Push a selected folder"
            echo ""
            echo "  dev push -f <files> -d <folder> <message>"
            echo "      Push selected files and folders"
            echo ""
            echo "  dev backup"
            echo "      Create a compressed project backup"
            echo ""
            echo "  dev backup <name>"
            echo "      Create a named project backup"
            echo ""
            echo "  dev serve"
            echo "      Start a local web server on port 8000"
            echo ""
            echo "  dev serve <port>"
            echo "      Start a local web server on the specified port"
            echo ""
            echo "  dev clone <username> <repository>"
            echo "      Clone a GitHub repository, create a .venv"
            echo "      and install requirements.txt if available"
            echo ""

            echo "  dev clone <username> <repository> <version>"
            echo "      Clone using a specific Python version"
            echo "      Example: dev clone octocat hello-world 3.12"
            echo ""

            ;;

        *)
            echo "Unknown command: $1"
            echo "Run 'dev' to see available commands."
            return 1
            ;;



    esac
}
