
# sad-automated-invoice

This project automates event management for GKDI Teens Ministry Sisters Appreciation Day. It detects new Google Form submissions, updates a database, and sends virtual invoices with dummy boarding passes to attendees. 







## Variables

To run this project, you will need to add the following variables to the code,

- `sheets_id` on `main.py`
- `login_email` on `./utils/__init__.py`
- `login_password` on `./utils/__init__.py`


## Deployment

This section outlines the steps to deploy the SAD Automated Invoice application using Docker.

Docker Engine: Ensure you have Docker installed and running on your system. Refer to the official Docker documentation for installation instructions: https://docs.docker.com/get-docker/


### Building the Docker Image


Clone the repository: If you haven't already, clone the repository containing the application code and Dockerfile.

Navigate to the project directory: Open your terminal or command prompt and navigate to the root directory of the project.

Build the image: Execute the following command to build the Docker image:
```bash
docker build -t sad-automated-invoice .
```

This command will build the image tagged as sad-automated-invoice using the Dockerfile present in the current directory (.).


### Running the Docker Container


Start the container: Once the image is built, you can start a container named sad-automated-mail in detached mode (running in the background) using the following command:
```bash
docker run --name sad-automated-mail -d sad-automated-invoice 
```
## License

[MIT](https://choosealicense.com/licenses/mit/)


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

