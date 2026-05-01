from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Aluno(Base):
    __tablename__ = "aluno"

    matricula = Column(Integer, primary_key=True)
    nome = Column(String(200))
    telefone = Column(String(11))  # ✅ agora correto


class Livro(Base):
    __tablename__ = "livro"

    id_livro = Column(Integer, primary_key=True)
    titulo = Column(String(300))


class Exemplar(Base):
    __tablename__ = "exemplar"

    id_exemplar = Column(Integer, primary_key=True)
    id_livro = Column(Integer, ForeignKey("livro.id_livro"))

    livro = relationship("Livro")


class Emprestimo(Base):
    __tablename__ = "emprestimo"

    id_emprestimo = Column(Integer, primary_key=True)

    id_exemplar = Column(Integer, ForeignKey("exemplar.id_exemplar"))
    matricula = Column(Integer, ForeignKey("aluno.matricula"))

    data_emprestimo = Column(Date)
    data_devolucao_prevista = Column(Date)
    data_devolucao_real = Column(Date)

    exemplar = relationship("Exemplar")
    aluno = relationship("Aluno")