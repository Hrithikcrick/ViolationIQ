"""Demo runner for ViolationIQ adaptive router."""

from src.adaptive_router import ViolationIQRouter

def main(input_path):
    router = ViolationIQRouter()
    route = router.route_by_input_type(input_path)
    print(route)

if __name__ == "__main__":
    main("sample_input.mp4")