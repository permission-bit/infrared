# nano ~/.zshrc
venv() {
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "No virtual environment found."
        return 1
    fi
}
# source ~/.zshrc



push() {
    files=()
    folders=()
    message=""

    while [ "$#" -gt 0 ]; do
        case "$1" in
            -f)
                shift
                while [ "$#" -gt 0 ] && [ "$1" != "-d" ] && [ "$1" != "-f" ]; do
                    if [ "$#" -eq 1 ]; then
                        message="$1"
                        break
                    fi
                    files+=("$1")
                    shift
                done
                ;;

            -d)
                shift
                while [ "$#" -gt 0 ] && [ "$1" != "-d" ] && [ "$1" != "-f" ]; do
                    if [ "$#" -eq 1 ]; then
                        message="$1"
                        break
                    fi
                    folders+=("$1")
                    shift
                done
                ;;

            *)
                message="$*"
                break
                ;;
        esac
        shift
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
}