# Eulerian Video Magnification (EVM)
Implementação local do método **Eulerian Video Magnification**, capaz de amplificar
movimentos sutis em vídeos — como a respiração de um bebê — que são invisíveis a olho nu.
## Técnica
O método utiliza:
- **Pirâmide Laplaciana** para decomposição espacial do vídeo
- **Filtro passa-banda temporal (FFT)** para isolar frequências de interesse
- **Amplificação** do sinal filtrado por nível da pirâmide
- **Reconstrução** do vídeo com os movimentos amplificados
## Referência
Wu, H., Rubinstein, M., Shih, E., Durand, F., Freeman, W. (2012).  
*Eulerian Video Magnification for Revealing Subtle Changes in the World.*  
ACM SIGGRAPH 2012.  
https://people.csail.mit.edu/mrub/evm/
## Estrutura do Projeto
├── src/ # Módulos Python (pirâmide, filtros, pipeline) 
├── videos/ 
│ ├── input/ # Vídeos de entrada 
│ └── output/ # Vídeos processados 
├── docs/ # Documentação e referências 
├── main.py # Ponto de entrada 
└── requirements.txt