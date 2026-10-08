from Brain import Brain

def main() -> None:
    try:
        Brain().run()
    except KeyboardInterrupt:
        print("\nAsmo -> Bye :<")
        
if __name__ == "__main__":
    main()