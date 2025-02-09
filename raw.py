import numpy as np

def analog_to_readable_txt(input_data, output_file, sampling_rate=None):
    """
    Convert analog data to a human-readable text file format.
    
    Parameters:
    input_data (list/array): Raw analog data values
    output_file (str): Name of the output text file
    sampling_rate (float, optional): Sampling rate in Hz
    """
    try:
        with open(output_file, 'w') as f:
            # Write header
            f.write("=== Analog Data Recording ===\n\n")
            
            if sampling_rate:
                f.write(f"Sampling Rate: {sampling_rate} Hz\n")
                f.write(f"Total Samples: {len(input_data)}\n")
                f.write(f"Recording Duration: {len(input_data)/sampling_rate:.2f} seconds\n\n")
            
            f.write("Reading #  |  Time (s)  |  Value\n")
            f.write("-" * 40 + "\n")
            
            # Write data
            for i, value in enumerate(input_data):
                if sampling_rate:
                    time = i / sampling_rate
                    f.write(f"{i+1:8d}  |  {time:8.3f}  |  {value:8.3f}\n")
                else:
                    f.write(f"{i+1:8d}  |     --     |  {value:8.3f}\n")
            
            # Write footer
            f.write("\n=== End of Recording ===\n")
        
        return True
        
    except Exception as e:
        print(f"Error writing data: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Sample data
    sample_data = [0.523, 1.234, 2.145, 1.832, 1.545, 0.923, 0.345]
    
    # Convert the data with sampling rate
    success = analog_to_readable_txt(sample_data, 'readable_analog_data.txt', sampling_rate=1000)
    
    if success:
        print("Data successfully converted to readable format!")
        print("Sample output file content:")
        with open('readable_analog_data.txt', 'r') as f:
            print(f.read())