import time
import random

class SharedCriticalComponent:
    """
    Simulates a shared library or critical component that all service instances depend on.
    It contains a latent software bug that triggers under specific conditions.
    Once triggered, it enters a failed state, affecting all consumers.
    """
    def __init__(self, name):
        self.name = name
        self._bug_triggered = False
        print(f"  [SharedComponent:{self.name}] Initialized.")

    def process_data(self, data):
        """
        This method contains the 'bug'. If a specific 'poison_pill' data is processed,
        it simulates a critical failure in the shared logic. Once the bug is triggered,
        the component becomes unstable for all subsequent calls.
        """
        if data == "POISON_PILL_DATA" and not self._bug_triggered:
            self._bug_triggered = True
            print(f"  [SharedComponent:{self.name}] !!! CRITICAL BUG TRIGGERED by '{data}' !!!")
            print(f"  [SharedComponent:{self.name}] This shared component is now in a failed state.")
            # In a real system, this might lead to a crash, resource exhaustion,
            # or corrupted state for anyone using it.
            raise ValueError("Critical shared component bug detected!")
        elif self._bug_triggered:
            # Once the bug is triggered, subsequent calls (even with normal data)
            # will also fail because the component is compromised.
            raise RuntimeError("Shared component is in a persistent failed state after bug trigger.")
        else:
            # Simulate normal processing
            # print(f"  [SharedComponent:{self.name}] Processing data: {data}")
            return f"Processed: {data}"

class ServiceInstance:
    """
    Represents a single service instance, part of a redundant setup across data centers.
    Each instance relies on a (potentially buggy) shared critical component.
    """
    def __init__(self, instance_id, data_center, shared_component):
        self.instance_id = instance_id
        self.data_center = data_center
        self.is_healthy = True
        # Key concept: All instances depend on the *same* shared_component object
        # or identical flawed code deployed across instances.
        self.shared_component = shared_component
        print(f"[{self.data_center}][Instance-{self.instance_id}] Initialized.")

    def handle_request(self, request_data):
        if not self.is_healthy:
            print(f"[{self.data_center}][Instance-{self.instance_id}] is UNHEALTHY. Cannot process request.")
            return "FAILURE: Instance unhealthy"

        try:
            # All instances execute logic that depends on the shared component
            result = self.shared_component.process_data(request_data)
            # print(f"[{self.data_center}][Instance-{self.instance_id}] Processed request: '{request_data}' -> '{result}'")
            return f"SUCCESS: {result}"
        except (ValueError, RuntimeError) as e:
            self.is_healthy = False
            print(f"[{self.data_center}][Instance-{self.instance_id}] CRITICAL FAILURE: {e}. Marking instance as UNHEALTHY.")
            return "FAILURE: Shared component failed"

    def get_status(self):
        return "HEALTHY" if self.is_healthy else "UNHEALTHY"

# --- Simulation Setup ---
def simulate_system():
    print("--- System Initialization ---")

    # The 'bug' is within the logic of SharedCriticalComponent. To demonstrate
    # a single point of failure *despite* redundancy, we simulate all instances
    # relying on the *same physical instance* of this critical component (e.g., a shared service,
    # a singleton library, or a common configuration loaded once and shared).
    common_buggy_component = SharedCriticalComponent("GlobalDataProcessor")

    instances = []
    num_instances_per_dc = 2
    data_centers = ["DC-EAST", "DC-WEST"]

    for dc in data_centers:
        for i in range(1, num_instances_per_dc + 1):
            instance_id = f"{dc}-{i}"
            # All instances are configured to use the *same* common_buggy_component object.
            # This is the hidden dependency that undermines redundancy.
            instances.append(ServiceInstance(instance_id, dc, common_buggy_component))

    print("\n--- Initial System Status ---")
    for instance in instances:
        print(f"[{instance.data_center}][Instance-{instance.instance_id}] Status: {instance.get_status()}")

    print("\n--- Simulating Normal Operations (Round 1) ---")
    for i, instance in enumerate(instances):
        request_data = f"normal_request_{i}"
        response = instance.handle_request(request_data)
        print(f"  Request to Instance-{instance.instance_id}: {response}")
        time.sleep(0.1)

    print("\n--- System Status After Normal Operations ---")
    for instance in instances:
        print(f"[{instance.data_center}][Instance-{instance.instance_id}] Status: {instance.get_status()}")

    print("\n--- Simulating a 'Poison Pill' Request (Triggering the Bug) ---")
    # Send a request that triggers the bug to *one* instance.
    # Because the `common_buggy_component` is a single object shared by all instances,
    # triggering the bug through one instance's interaction affects the shared component's state,
    # thus impacting all other instances.
    trigger_instance = instances[random.randint(0, len(instances) - 1)] # Pick a random instance to get the bad request
    print(f"Sending 'POISON_PILL_DATA' to [{trigger_instance.data_center}][Instance-{trigger_instance.instance_id}]...")
    trigger_response = trigger_instance.handle_request("POISON_PILL_DATA")
    print(f"  Response from Trigger Instance: {trigger_response}")

    print("\n--- System Status Immediately After Bug Trigger ---")
    for instance in instances:
        print(f"[{instance.data_center}][Instance-{instance.instance_id}] Status: {instance.get_status()}")

    print("\n--- Simulating Subsequent Operations (After Bug Trigger) ---")
    # Now, even if other instances get normal requests, they will fail
    # because the shared component is now in a failed state.
    for i, instance in enumerate(instances):
        request_data = f"subsequent_normal_request_{i}"
        response = instance.handle_request(request_data)
        print(f"  Request to Instance-{instance.instance_id}: {response}")
        time.sleep(0.1)

    print("\n--- Final System Status ---")
    all_unhealthy = True
    for instance in instances:
        status = instance.get_status()
        print(f"[{instance.data_center}][Instance-{instance.instance_id}] Status: {status}")
        if status == "HEALTHY":
            all_unhealthy = False

    if all_unhealthy:
        print("\n!!! All instances across both data centers are UNHEALTHY. Single bug, big collapse. !!!")
    else:
        print("\nSome instances are still healthy. The collapse was not total.")


if __name__ == "__main__":
    simulate_system()
