# Nocto

<!-- Full window width, keeps aspect ratio -->
<img src="docs/nocto-logo.svg" alt="Nocto Logo" style="width:100%; height:auto; display:block;" />

<h3 align="center"><b>An International Emergency Alerting Platform</b></h3>

---

## Overview

Nocto is a comprehensive international alerting application designed to monitor and display currently active weather and civil emergency alerts from government sources worldwide. The platform provides real-time visibility into ongoing safety situations by interfacing with official public APIs maintained by national governments.

## Key Features

- **Global Alert Monitoring**: View currently active emergency alerts from multiple countries through a unified interface
- **Real-time Status Updates**: Live monitoring of active government alert systems
- **AI-Enhanced Content**: Automated summarization and translation of active alerts for improved accessibility
- **Extensible Architecture**: Modular design allows for easy integration of new countries and alert sources

## Architecture

Nocto is built on a robust backend architecture that utilizes official government APIs. The application serves as an example implementation using Germany's [NINA API](https://nina.api.bund.dev), which demonstrates best practices for structured, open emergency alert systems.

## Contributing

### Adding New Countries

Contributors can extend Nocto's coverage by implementing support for additional countries:

1. Create a new Python module in the appropriate directory
2. Implement the `CountryBackend` interface for your target country
3. Configure the API endpoints and data mapping for the country's alert system
4. Submit a pull request with comprehensive documentation

### Development Requirements

Nocto requires the following dependencies:

```
folium>=0.20.0
shapely>=2.1.1
starlette>=0.47.2
uvicorn>=0.35.0
```

## Getting Started

### Installation and Setup

1. Clone the repository
2. Install dependencies using your preferred package manager
3. Configure any required API keys or endpoints

### Running the Application

Execute the following command to start the development server:

```bash
uv run uvicorn --app-dir src main:app
```

The application will be available at the default uvicorn address.

## AI Integration

Nocto incorporates artificial intelligence capabilities to enhance user experience with active alerts:

- **Alert Summarization**: AI-powered summarization of complex emergency communications currently in effect
- **Multi-language Translation**: Automatic translation of foreign language alerts to improve international accessibility
- **Content Enhancement**: Intelligent processing to standardize active alert formatting across different government systems

## Project Status

Nocto is actively under development with ongoing implementation of additional countries and alert sources. The project maintains a roadmap of planned features and supported regions.

## License
This project is Licensed under the BSD-3-Clause license
```
Copyright 2025 NotNekodev and Contributors

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```