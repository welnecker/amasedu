    if st.button("📤 Enviar Respostas"):
        if any(r is None for r in respostas.values()):
            st.warning("⚠️ Há questões não respondidas.")
            st.stop()

        try:
            gabarito_df = carregar_gabarito()
            acertos = 0
            acertos_detalhe = {}
            linha_envio = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), codigo_atividade, nome_aluno, escola, turma]

            for atividade, resposta in respostas.items():
                linha_gabarito = gabarito_df[gabarito_df["ATIVIDADE"] == atividade]
                gabarito = linha_gabarito["GABARITO"].values[0] if not linha_gabarito.empty else "?"
                situacao = "Certo" if resposta.upper() == gabarito.upper() else "Errado"
                if situacao == "Certo":
                    acertos += 1
                acertos_detalhe[atividade] = situacao
                linha_envio.extend([atividade, resposta, situacao])

            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            service = build("sheets", "v4", credentials=creds)

            service.spreadsheets().values().append(
                spreadsheetId="17SUODxQqwWOoC9Bns--MmEDEruawdeEZzNXuwh3ZIj8",
                range="ATIVIDADES!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [linha_envio]}
            ).execute()

            st.session_state.respostas_enviadas.add(id_unico)
            st.session_state.respostas_salvas[id_unico] = acertos_detalhe
            st.success(f"✅ Respostas enviadas! Você acertou {acertos}/{len(respostas)}.")
        
        except Exception as e:
            st.error(f"Erro ao enviar respostas: {e}")

        if id_unico in st.session_state.respostas_salvas:
            acertos_detalhe = st.session_state.respostas_salvas[id_unico]
            st.markdown("---")
            for idx, atividade in enumerate(atividades):
                situacao = acertos_detalhe.get(atividade, "❓")
                cor = "✅" if situacao == "Certo" else "❌"
                st.markdown(f"**Atividade {idx+1}:** {cor}")
            st.markdown("---")
            if st.button("🔄 Limpar Atividade"):
                del st.session_state["atividades_em_exibicao"]
                st.rerun()
