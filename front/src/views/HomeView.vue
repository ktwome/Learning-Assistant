<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card class="pa-6 text-center" max-width="640" elevation="4">
      <v-card-title class="text-h5 font-weight-bold mb-2">
        📚 학습 보조 서비스
      </v-card-title>
      <v-card-text class="mb-6">
        PDF 강의자료를 정돈된 Markdown 문서로 변환하거나,<br />
        이전에 변환한 문서를 다시 확인할 수 있습니다.
      </v-card-text>

      <v-row dense>
        <v-col cols="12" sm="6">
          <v-card
            color="blue-lighten-5"
            variant="outlined"
            class="hover-card"
            @click="goUpload"
          >
            <v-card-title class="text-subtitle-1 font-weight-bold">📤 PDF 업로드</v-card-title>
            <v-card-text class="text-body-2">새로운 PDF를 업로드하고 변환을 시작합니다.</v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6">
          <v-card
            color="green-lighten-5"
            variant="outlined"
            class="hover-card"
            @click="goDocs"
          >
            <v-card-title class="text-subtitle-1 font-weight-bold">📑 저장된 목록</v-card-title>
            <v-card-text class="text-body-2">이전에 변환한 Markdown 파일들을 조회합니다.</v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
    goUpload() {
      this.$router.push('/upload')
    },
    goDocs() {
      this.$router.push('/view')
    }
  }
}
</script>

<style scoped>
.fill-height {
  min-height: calc(100vh - 64px);
}
.hover-card {
  transition: 0.3s ease;
  cursor: pointer;
}
.hover-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}
</style>
