<template>
  <v-container>
    <v-card>
      <v-card-title>API 종류를 선택하세요</v-card-title>
      <v-card-actions>
        <v-btn color="primary" @click="goUpload">PDF 업로드</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
    goUpload() {
      this.$router.push('/upload')
    }
  }
}
</script>
