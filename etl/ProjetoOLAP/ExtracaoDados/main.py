import pandas as pd

from Extrair.extrair_dim_produto import extrair_dim_produto
from Extrair.extrair_dim_cliente import extrair_dim_cliente
from Extrair.extrair_dim_territorio import extrair_dim_territorio
from Extrair.extrair_dim_data import extrair_dim_data
from Extrair.extrair_fato_vendas import extrair_fato_vendas


from controle.buscar_chaves_dimensoes import buscar_chaves_dimensoes

from controle.buscar_controle_etl import (
    buscar_ultima_execucao,
    atualizar_ultima_execucao
)


from identificador_incremental.identificar_incremental_produto import (
    identificar_incremental_produto
)

from identificador_incremental.identificar_incremental_cliente import (
    identificar_incremental_cliente
)

from identificador_incremental.identificar_incremental_territorio import (
    identificar_incremental_territorio
)

from identificador_incremental.identificar_incremental_data import (
    identificar_incremental_data
)

from identificador_incremental.identificar_incremental_fato import (
    identificar_incremental_fato
)


from transformacao.transformar_dim_produto import transformar_dim_produto
from transformacao.transformar_dim_cliente import transformar_dim_cliente
from transformacao.transformar_dim_territorio import transformar_dim_territorio
from transformacao.transformar_dim_data import transformar_dim_data
from transformacao.transformar_fato_vendas import transformar_fato_vendas


from carregamento.carregar_dim_produto import carregar_dim_produto
from carregamento.carregar_dim_cliente import carregar_dim_cliente
from carregamento.carregar_dim_territorio import carregar_dim_territorio
from carregamento.carregar_dim_data import carregar_dim_data
from carregamento.carregar_fato_vendas import carregar_fato_vendas


def main():

    # ==========================================
    # INÍCIO DO ETL
    # ==========================================

    print("\n================================")
    print("INICIANDO ETL")
    print("================================")


    # ==========================================
    # 1. DIM_PRODUTO - ETL INCREMENTAL
    # ==========================================

    print("\n================================")
    print("ETL INCREMENTAL - DIM_PRODUTO")
    print("================================")

    data_controle_produto = buscar_ultima_execucao(
        "dim_produto"
    )

    print(f"Data de controle: {data_controle_produto}")

    print("\nExtraindo produtos alterados...")

    df_produto = extrair_dim_produto(
        data_controle_produto
    )

    print(f"Registros extraídos: {len(df_produto)}")

    if not df_produto.empty:

        df_produto_novos, df_produto_alterados = (
            identificar_incremental_produto(
                df_produto,
                data_controle_produto
            )
        )

        print(
            f"Produtos novos: "
            f"{len(df_produto_novos)}"
        )

        print(
            f"Produtos alterados: "
            f"{len(df_produto_alterados)}"
        )

        carregar_dim_produto(
            df_produto_novos,
            df_produto_alterados
        )

        maior_data = df_produto["ModifiedDate"].max()

        atualizar_ultima_execucao(
            "dim_produto",
            maior_data
        )

        print("\n================================")
        print("CONTROLE PRODUTO ATUALIZADO")
        print("================================")

        print(
            f"Nova data de controle: "
            f"{maior_data}"
        )

    else:

        print("\nNenhum produto novo ou alterado.")


    # ==========================================
    # 2. DIM_CLIENTE - ETL INCREMENTAL
    # ==========================================

    print("\n================================")
    print("ETL INCREMENTAL - DIM_CLIENTE")
    print("================================")

    data_controle_cliente = buscar_ultima_execucao(
        "dim_cliente"
    )

    print(f"Data de controle: {data_controle_cliente}")

    print("\nExtraindo clientes alterados...")

    df_cliente = extrair_dim_cliente(
        data_controle_cliente
    )

    print(f"Registros extraídos: {len(df_cliente)}")

    if not df_cliente.empty:

        df_cliente_novos, df_cliente_alterados = (
            identificar_incremental_cliente(
                df_cliente,
                data_controle_cliente
            )
        )

        print(
            f"Clientes novos: "
            f"{len(df_cliente_novos)}"
        )

        print(
            f"Clientes alterados: "
            f"{len(df_cliente_alterados)}"
        )

        carregar_dim_cliente(
            df_cliente_novos,
            df_cliente_alterados
        )

        maior_data = df_cliente["ModifiedDate"].max()

        atualizar_ultima_execucao(
            "dim_cliente",
            maior_data
        )

        print("\n================================")
        print("CONTROLE CLIENTE ATUALIZADO")
        print("================================")

        print(
            f"Nova data de controle: "
            f"{maior_data}"
        )

    else:

        print("\nNenhum cliente novo ou alterado.")


    # ==========================================
    # 3. DIM_TERRITORIO - ETL INCREMENTAL
    # ==========================================

    print("\n================================")
    print("ETL INCREMENTAL - DIM_TERRITORIO")
    print("================================")

    data_controle_territorio = buscar_ultima_execucao(
        "dim_territorio"
    )

    print(
        f"Data de controle: "
        f"{data_controle_territorio}"
    )

    print("\nExtraindo territórios alterados...")

    df_territorio = extrair_dim_territorio(
        data_controle_territorio
    )

    print(
        f"Registros extraídos: "
        f"{len(df_territorio)}"
    )

    if not df_territorio.empty:

        (
            df_territorio_novos,
            df_territorio_alterados
        ) = identificar_incremental_territorio(
            df_territorio,
            data_controle_territorio
        )

        print(
            f"Territórios novos: "
            f"{len(df_territorio_novos)}"
        )

        print(
            f"Territórios alterados: "
            f"{len(df_territorio_alterados)}"
        )

        carregar_dim_territorio(
            df_territorio_novos,
            df_territorio_alterados
        )

        maior_data = df_territorio["ModifiedDate"].max()

        atualizar_ultima_execucao(
            "dim_territorio",
            maior_data
        )

        print("\n================================")
        print("CONTROLE TERRITÓRIO ATUALIZADO")
        print("================================")

        print(
            f"Nova data de controle: "
            f"{maior_data}"
        )

    else:

        print("\nNenhum território novo ou alterado.")


    # ==========================================
    # 4. DIM_DATA - ETL INCREMENTAL
    # ==========================================

    print("\n================================")
    print("ETL INCREMENTAL - DIM_DATA")
    print("================================")


    # ------------------------------------------
    # EXTRAÇÃO
    # ------------------------------------------

    print("\nExtraindo calendário...")

    df_data = extrair_dim_data()

    print(
        f"Datas geradas: "
        f"{len(df_data)}"
    )


    # ------------------------------------------
    # TRANSFORMAÇÃO
    # ------------------------------------------

    df_data = transformar_dim_data(
        df_data
    )

    print(
        f"Datas transformadas: "
        f"{len(df_data)}"
    )


    # ------------------------------------------
    # IDENTIFICAR DATAS NOVAS
    # ------------------------------------------

    df_data_novas = identificar_incremental_data(
        df_data
    )

    print(
        f"Datas novas: "
        f"{len(df_data_novas)}"
    )


    # ------------------------------------------
    # CARGA
    # ------------------------------------------

    if not df_data_novas.empty:

        carregar_dim_data(
            df_data_novas
        )

        print("Novas datas carregadas.")

    else:

        print("Nenhuma data nova para carregar.")


    # ==========================================
    # 5. FATO_VENDAS - ETL INCREMENTAL
    # ==========================================

    print("\n================================")
    print("ETL INCREMENTAL - FATO_VENDAS")
    print("================================")


    # ------------------------------------------
    # 1. Buscar data de controle
    # ------------------------------------------

    data_controle_fato = buscar_ultima_execucao(
        "fato_vendas"
    )

    print(
        f"\nData de controle: "
        f"{data_controle_fato}"
    )


    # ------------------------------------------
    # 2. Extração incremental
    # ------------------------------------------

    print("\nExtraindo vendas...")

    df_vendas = extrair_fato_vendas(
        data_controle_fato
    )

    print(
        f"Registros extraídos: "
        f"{len(df_vendas)}"
    )


    # ------------------------------------------
    # 3. Verificar se existem alterações
    # ------------------------------------------

    if df_vendas.empty:

        print(
            "\nNenhuma venda nova ou alterada."
        )

    else:

        # --------------------------------------
        # 4. Identificar INSERT e UPDATE
        # --------------------------------------

        (
            df_vendas_novas,
            df_vendas_alteradas
        ) = identificar_incremental_fato(
            df_vendas,
            data_controle_fato
        )

        print(
            f"\nVendas novas: "
            f"{len(df_vendas_novas)}"
        )

        print(
            f"Vendas alteradas: "
            f"{len(df_vendas_alteradas)}"
        )


        # --------------------------------------
        # 5. Buscar chaves das dimensões
        # --------------------------------------

        print(
            "\nBuscando chaves das dimensões..."
        )

        (
            df_produto,
            df_cliente,
            df_territorio,
            df_data
        ) = buscar_chaves_dimensoes()


        # --------------------------------------
        # 6. Transformar vendas novas
        # --------------------------------------

        if not df_vendas_novas.empty:

            df_vendas_novas = (
                transformar_fato_vendas(
                    df_vendas_novas,
                    df_produto,
                    df_cliente,
                    df_territorio,
                    df_data
                )
            )


        # --------------------------------------
        # 7. Transformar vendas alteradas
        # --------------------------------------

        if not df_vendas_alteradas.empty:

            df_vendas_alteradas = (
                transformar_fato_vendas(
                    df_vendas_alteradas,
                    df_produto,
                    df_cliente,
                    df_territorio,
                    df_data
                )
            )


        # --------------------------------------
        # 8. Verificar chaves das dimensões
        # --------------------------------------

        erro_chaves = False


        if not df_vendas_novas.empty:

            if (
                df_vendas_novas["produto_key"].isna().any()
                or df_vendas_novas["cliente_key"].isna().any()
                or df_vendas_novas["territorio_key"].isna().any()
                or df_vendas_novas["data_key"].isna().any()
            ):

                erro_chaves = True


        if not df_vendas_alteradas.empty:

            if (
                df_vendas_alteradas["produto_key"].isna().any()
                or df_vendas_alteradas["cliente_key"].isna().any()
                or df_vendas_alteradas["territorio_key"].isna().any()
                or df_vendas_alteradas["data_key"].isna().any()
            ):

                erro_chaves = True


        # --------------------------------------
        # 9. Carregar no DW
        # --------------------------------------

        if erro_chaves:

            print("\nERRO:")
            print(
                "Existem vendas sem chave "
                "correspondente nas dimensões."
            )

            print(
                "A carga da fato foi cancelada."
            )

        else:

            carregar_fato_vendas(
                df_vendas_novas,
                df_vendas_alteradas
            )


            # ----------------------------------
            # 10. Atualizar controle
            # ----------------------------------

            maior_data = pd.to_datetime(
                df_vendas["ModifiedDate"]
            ).max()

            atualizar_ultima_execucao(
                "fato_vendas",
                maior_data
            )

            print(
                f"\nControle atualizado para: "
                f"{maior_data}"
            )


    # ==========================================
    # FINALIZAÇÃO
    # ==========================================

    print("\n================================")
    print("ETL FINALIZADO")
    print("================================")


if __name__ == "__main__":
    main()