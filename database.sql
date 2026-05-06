CREATE DATABASE busca_semantica;

CREATE TABLE metadata_table (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(50),
    data_imagem DATE,
    origem VARCHAR(50),
    arquivo VARCHAR(255)
);

INSERT INTO metadata_table (categoria, data_imagem, origem, arquivo)
VALUES

('vegetação', '2026-05-01', 'satélite', 'static/images/vegetacao/vegetacao1.jpg'),
('vegetação', '2026-05-02', 'drone', 'static/images/vegetacao/vegetacao2.jpg'),
('vegetação', '2026-05-03', 'satélite', 'static/images/vegetacao/vegetacao3.jpg'),
('vegetação', '2026-05-04', 'drone', 'static/images/vegetacao/vegetacao4.jpg'),
('vegetação', '2026-05-05', 'satélite', 'static/images/vegetacao/vegetacao5.jpg'),

('água', '2026-05-06', 'drone', 'static/images/agua/agua1.jpg'),
('água', '2026-05-07', 'satélite', 'static/images/agua/agua2.jpg'),
('água', '2026-05-08', 'drone', 'static/images/agua/agua3.jpg'),
('água', '2026-05-09', 'satélite', 'static/images/agua/agua4.jpg'),
('água', '2026-05-10', 'drone', 'static/images/agua/agua5.jpg'),

('solo exposto', '2026-05-11', 'satélite', 'static/images/solo_exposto/solo_exposto1.jpg'),
('solo exposto', '2026-05-12', 'drone', 'static/images/solo_exposto/solo_exposto2.jpg'),
('solo exposto', '2026-05-13', 'satélite', 'static/images/solo_exposto/solo_exposto3.jpg'),
('solo exposto', '2026-05-14', 'drone', 'static/images/solo_exposto/solo_exposto4.jpg'),
('solo exposto', '2026-05-15', 'satélite', 'static/images/solo_exposto/solo_exposto5.jpg');