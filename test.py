import pyRserve
import os

def test_rserve_connection():
    directory = os.getcwd()
    chart_path = os.path.join(directory,"graphs","r_generated_chart.png").replace("\\", "/")
    try:
        # Connect to Rserve (use the correct port if different from 6311)
        conn = pyRserve.connect(host='localhost', port=6315)
        print("Connected to Rserve successfully!")
        r_script = f"""
library(ggplot2)
dir.create(dirname("{chart_path}"), showWarnings = FALSE)
data <- data.frame(
    time = 1:100,
    price = cumsum(rnorm(100, 0, 1)) + 50
)
p <- ggplot(data, aes(x = time, y = price)) +
    geom_line(color = "blue", linewidth = 1) + 
    labs(title = "Bitcoin Price Chart", x = "Time", y = "Price") +
    theme_minimal()
ggsave("{chart_path}",plot = p, width = 8, height = 4)
"""
        conn.eval(r_script)

        # Close the connection
        conn.close()
        print("Connection closed successfully.")
    except Exception as e:
        print(f"Error interacting with Rserve: {e}")

if __name__ == "__main__":
    test_rserve_connection()
    
        #     directory = os.getcwd()
        # chart_path = os.path.join(directory,"graphs","r_generated_chart.png").replace("\\", "/")