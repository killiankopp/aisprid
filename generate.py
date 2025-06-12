import csv
import datetime
import random
import json
import uuid # For unique error IDs

class ErrorSimulator:
    def __init__(self):
        self.active_errors = []  # List of current error dicts {Id, CreatedAtTs, Type}
        self.error_history = []  # List of ErrorStatus dicts {Status_Ts, Active_Errors_Snapshot}
        # Initialize simulation time slightly in the past to make increments clear
        self.current_sim_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24) # Start further back for longer simulation
        self.error_types = ["hardware", "bad_usage", "bug"]

        # Record initial state (no errors) at the start time
        self._record_status_change(self.current_sim_time)

    def _get_iso_timestamp(self, dt_object):
        return dt_object.isoformat()

    def _record_status_change(self, status_timestamp):
        # Deep copy the current errors to avoid modification issues later
        errors_snapshot = [dict(e) for e in self.active_errors]
        self.error_history.append({
            "Status_Ts": self._get_iso_timestamp(status_timestamp),
            "Active_Errors": errors_snapshot 
        })
        # Optional: print when a status is recorded for debugging/visibility
        # print(f"--- Status Recorded at {self._get_iso_timestamp(status_timestamp)}: {len(errors_snapshot)} active errors ---")


    def add_error(self, event_timestamp):
        error_id = str(uuid.uuid4()) # Generate a unique ID for the error
        error_created_at_ts = self._get_iso_timestamp(event_timestamp)
        error_type = random.choice(self.error_types)
        
        new_error = {
            "Id": error_id,
            "CreatedAtTs": error_created_at_ts,
            "Type": error_type
        }
        self.active_errors.append(new_error)
        self._record_status_change(event_timestamp) # Record state change at event_timestamp
        print(f"{self._get_iso_timestamp(event_timestamp)}: ADDED Error ID {error_id} ({error_type}). Active errors: {len(self.active_errors)}")

    def clear_error(self, event_timestamp):
        if not self.active_errors:
            return False 

        error_to_remove = random.choice(self.active_errors)
        self.active_errors.remove(error_to_remove)
        self._record_status_change(event_timestamp) # Record state change at event_timestamp
        print(f"{self._get_iso_timestamp(event_timestamp)}: CLEARED Error ID {error_to_remove['Id']}. Active errors: {len(self.active_errors)}")
        return True

    def simulate(self, num_event_opportunities=100, max_time_increment_seconds=3600):
        """
        Simulates a series of error events.
        num_event_opportunities: The number of chances for an event (add/clear) to occur.
        max_time_increment_seconds: Maximum number of seconds to advance time for each opportunity.
        """
        print(f"Initial state recorded at {self.error_history[0]['Status_Ts']}: No errors. Active: {len(self.error_history[0]['Active_Errors'])}")

        # --- Probabilities for controlling error frequency ---
        # Probability of an error occurring when the system is currently clear
        prob_add_error_when_clear = 0.01  # e.g., 5% chance (much lower than before)
        
        # When errors are active:
        # Probability of adding *another* error (vs. clearing one)
        prob_add_another_error_when_active = 0.1 # e.g., 10% chance to add, so 90% chance to clear

        for event_i in range(num_event_opportunities):
            # Advance simulation time for the current event opportunity
            # Make time increments potentially larger to simulate longer "all clear" periods
            time_increment_seconds = random.randint(60, max_time_increment_seconds) # Min 1 minute
            self.current_sim_time += datetime.timedelta(seconds=time_increment_seconds)
            event_timestamp = self.current_sim_time

            if not self.active_errors:
                # System is currently clear
                if random.random() < prob_add_error_when_clear:
                    self.add_error(event_timestamp)
                # else: No error added, system remains clear. 
                # No status change is recorded if no error is added, which aligns with
                # the idea that ErrorStatus reflects changes in the error array.
                # Time simply advances.
            else:
                # Errors are currently active
                if random.random() < prob_add_another_error_when_active:
                    # Less likely to add another error if some are already active
                    self.add_error(event_timestamp) 
                else:
                    # More likely to clear an existing error
                    self.clear_error(event_timestamp)
            
            # Small delay for readability of console output if running many events
            # import time
            # time.sleep(0.01) 
        
        print(f"\nSimulation finished. Total {len(self.error_history)} status changes recorded over {num_event_opportunities} opportunities.")

    def generate_csv(self, filename="simulated_error_status_fewer_errors.csv"):
        if not self.error_history:
            print("No history to generate CSV.")
            return

        fieldnames = ["Status_Ts", "Active_Errors_Count", "Active_Errors_Details_JSON"]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for status_entry in self.error_history:
                writer.writerow({
                    "Status_Ts": status_entry["Status_Ts"],
                    "Active_Errors_Count": len(status_entry["Active_Errors"]),
                    "Active_Errors_Details_JSON": status_entry["Active_Errors"]
                })
        print(f"CSV generated: {filename}")

# --- Main execution ---
if __name__ == "__main__":
    simulator = ErrorSimulator()
    
    # Simulate with more event opportunities but lower probabilities for errors
    # This should result in longer periods of no errors.
    simulator.simulate(num_event_opportunities=20000, max_time_increment_seconds=7200) # e.g., 200 opportunities, up to 2 hours apart
    
    simulator.generate_csv("simulated_error_logs.csv")
