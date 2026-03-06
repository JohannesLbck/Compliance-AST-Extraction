from generate_dataset import TEXT_MAPPING

def main():
    total = 0
    for key, text in TEXT_MAPPING.items():
        length = len(text)
        total += length
        print(f"{key}: {length} characters")
    avg = total / len(TEXT_MAPPING) if TEXT_MAPPING else 0
    print(f"\nAverage length: {avg:.1f} characters")

if __name__ == "__main__":
    main()