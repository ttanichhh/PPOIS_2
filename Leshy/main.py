import sys

from studio.movie_studio import MovieStudio
from studio.exceptions import StudioError


def print_header():
    print("\n" + "=" * 40)
    print("      MOVIE STUDIO MANAGEMENT SYSTEM      ")
    print("=" * 40)


def print_menu():
    print("\n--- RESOURCES & STAFF ---")
    print("1. Hire Director")
    print("2. Hire Actor")
    print("3. Buy Camera")
    print("4. Build Movie Set")

    print("\n--- PRODUCTION PIPELINE ---")
    print("5. Create Script (Start New Project)")
    print("6. Perform Casting")
    print("7. Start Filming")
    print("8. Run Post-Production")
    print("9. Release Movie")

    print("\n--- SYSTEM ---")
    print("0. Exit")
    print("10. Show Studio Status")


def main():
    studio = MovieStudio("Hollywood 2.0")

    print("Initializing system...")
    studio.hire_director("Christopher Nolan", "Sci-Fi")
    studio.hire_actor("Leonardo DiCaprio", "Star")
    studio.buy_camera("IMAX 70mm", "18K")
    studio.build_set("Los Angeles Street", False)

    while True:
        print_menu()
        choice = input("\nSelect option > ")

        try:
            if choice == "0":
                print("Shutting down system. Goodbye!")
                sys.exit()

            elif choice == "1":
                name = input("Director Name: ")
                style = input("Style (e.g. Drama, Horror): ")
                studio.hire_director(name, style)
                print(f"[OK] Director {name} hired.")

            elif choice == "2":
                name = input("Actor Name: ")
                rank = input("Rank (Novice, Star): ")
                studio.hire_actor(name, rank)
                print(f"[OK] Actor {name} hired.")

            elif choice == "3":
                model = input("Camera Model: ")
                res = input("Resolution (4K, 8K): ")
                studio.buy_camera(model, res)
                print(f"[OK] Camera {model} purchased.")

            elif choice == "4":
                loc = input("Location Name: ")
                indoor_input = input("Is Indoor? (y/n): ").lower()
                is_indoor = True if indoor_input == 'y' else False
                studio.build_set(loc, is_indoor)
                print(f"[OK] Set '{loc}' constructed.")

            elif choice == "5":
                title = input("Script Title: ")
                genre = input("Genre: ")
                pages = int(input("Number of Pages: "))

                new_id = studio.create_script(title, genre, pages)
                print(f"[OK] Project started! Movie ID: {new_id}")


            elif choice == "6":
                m_id = int(input("Movie ID: "))
                d_id = int(input("Director ID (see status): "))

                actors_input = input("Actor IDs (space separated, e.g. '0 1 2'): ")
                if not actors_input.strip():
                    a_ids = []
                else:
                    a_ids = [int(x) for x in actors_input.split()]

                studio.perform_casting(m_id, d_id, a_ids)
                print("[OK] Casting completed successfully.")

            elif choice == "7":
                m_id = int(input("Movie ID: "))
                c_id = int(input("Camera ID: "))
                s_id = int(input("Set ID: "))

                studio.start_filming(m_id, c_id, s_id)
                print("[OK] Filming started.")

            elif choice == "8":
                m_id = int(input("Movie ID: "))
                studio.run_post_production(m_id)
                print("[OK] Post-production finished.")

            elif choice == "9":
                m_id = int(input("Movie ID: "))
                studio.release_movie(m_id)
                print("[SUCCESS] Movie released!")

            elif choice == "10":
                print_header()
                print(f"STUDIO: {studio._name}")

                print("\n[MOVIES]")
                if not studio.movies: print("  No movies yet.")
                for i, m in enumerate(studio.movies):
                    print(f"  [{i}] {m}")

                print("\n[DIRECTORS]")
                for i, d in enumerate(studio._directors):
                    print(f"  [{i}] {d}")

                print("\n[ACTORS]")
                for i, a in enumerate(studio._actors):
                    print(f"  [{i}] {a}")

                print("\n[CAMERAS]")
                for i, c in enumerate(studio._cameras):
                    print(f"  [{i}] {c}")

                print("\n[SETS]")
                for i, s in enumerate(studio._sets):
                    print(f"  [{i}] {s}")

            else:
                print("[ERROR] Invalid selection.")

        except ValueError as ve:
            print(f"\n[INPUT ERROR] Invalid data format: {ve}")
        except StudioError as se:
            print(f"\n[STUDIO LOGIC ERROR] {se}")
        except Exception as e:
            print(f"\n[SYSTEM CRASH] Unexpected error: {e}")


if __name__ == "__main__":
    main()