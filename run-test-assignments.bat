pacers.py test-assignments\c-assignment-1
pacers.py test-assignments\c-assignment-2 --user-input "1 2" "3 4"
pacers.py test-assignments\c-assignment-3 --user-input "2 5" "10 20"
pacers.py test-assignments\c-assignment-4 --user-input "2 5" "10 20"

pacers.py test-assignments\txt-assignment-1

pacers.py test-assignments\cmake-assignment-1

pacers.py test-assignments\vcxproj-assignment-1

pacers.py test-assignments\vcxproj-GUI-assignment-1 --build-only --exclude-patterns SDL2-2.0.4/*
pacers.py test-assignments\vcxproj-GUI-assignment-1 --run-only-serial --timeout 0 --exclude-patterns SDL2-2.0.4/*
