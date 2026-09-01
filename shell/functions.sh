# nano ~/.zshrc

# source ~/.zshrc

dev() {
    case "$1" in

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
            ;;

        *)
            echo "Unknown command: $1"
            echo "Run 'dev' to see available commands."
            return 1
            ;;

    esac
}
