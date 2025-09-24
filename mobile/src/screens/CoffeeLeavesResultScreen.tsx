import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
} from 'react-native';
import {
  Surface,
  Text,
  Card,
  List,
  Chip,
  Button,
  ActivityIndicator,
} from 'react-native-paper';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useGetCoffeeLeavesAnalysisQuery } from '../services/coffeeLeavesApi';
import ImageViewer from '../components/ImageViewer';

export default function CoffeeLeavesResultScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation();
  const { analysisId } = route.params;
  const [imageViewerVisible, setImageViewerVisible] = useState(false);
  
  const { data: analysis, isLoading, error } = useGetCoffeeLeavesAnalysisQuery(analysisId);

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" />
        <Text variant="bodyLarge" style={styles.loadingText}>
          Loading analysis results...
        </Text>
      </View>
    );
  }

  if (error || !analysis) {
    return (
      <View style={styles.centerContainer}>
        <Text variant="bodyLarge">Failed to load analysis results</Text>
        <Button mode="contained" onPress={() => navigation.goBack()} style={styles.button}>
          Go Back
        </Button>
      </View>
    );
  }

  const healthScore = analysis.analysis?.health_score || 0;
  const scoreColor = healthScore >= 80 ? '#10B981' : healthScore >= 60 ? '#F59E0B' : '#EF4444';

  return (
    <ScrollView style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <Text variant="titleLarge">Analysis Results</Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Coffee Leaves Health Report
        </Text>
      </Surface>

      {analysis.image_url && (
        <TouchableOpacity onPress={() => setImageViewerVisible(true)}>
          <Card style={styles.card}>
            <Card.Cover source={{ uri: analysis.image_url }} style={styles.image} />
            <View style={styles.imageOverlay}>
              <Text variant="bodySmall" style={styles.tapToViewText}>
                Tap to view full image
              </Text>
            </View>
          </Card>
        </TouchableOpacity>
      )}

      <Card style={[styles.card, styles.scoreCard]}>
        <Card.Content>
          <View style={styles.scoreContainer}>
            <View style={[styles.scoreCircle, { borderColor: scoreColor }]}>
              <Text variant="headlineSmall" style={[styles.score, { color: scoreColor }]}>
                {healthScore.toFixed(1)}%
              </Text>
            </View>
            <Text variant="titleMedium" style={styles.scoreLabel}>
              Health Score
            </Text>
            <View style={styles.qualityIndicator}>
              <View style={[styles.qualityBar, { backgroundColor: '#E5E7EB' }]} />
              <View 
                style={[
                  styles.qualityBarFill, 
                  { 
                    backgroundColor: scoreColor,
                    width: `${healthScore}%` 
                  }
                ]} 
              />
            </View>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.sectionTitle}>
            Leaf Analysis
          </Text>
          <List.Item
            title="Total Leaves"
            description={`${analysis.analysis?.total_leaves || 0} leaves analyzed`}
            left={(props) => <List.Icon {...props} icon="leaf" />}
            titleStyle={styles.listItemTitle}
            descriptionStyle={styles.listItemDescription}
          />
          <List.Item
            title="Healthy Leaves"
            description={`${(analysis.analysis?.total_leaves || 0) - (analysis.analysis?.infected_leaves || 0)} leaves (${(((analysis.analysis?.total_leaves || 0) - (analysis.analysis?.infected_leaves || 0)) / (analysis.analysis?.total_leaves || 1) * 100).toFixed(1)}%)`}
            left={(props) => <List.Icon {...props} icon="check-circle" color="#10B981" />}
            titleStyle={styles.listItemTitle}
            descriptionStyle={[styles.listItemDescription, { color: '#10B981' }]}
          />
          <List.Item
            title="Infected Leaves"
            description={`${analysis.analysis?.infected_leaves || 0} leaves (${((analysis.analysis?.infected_leaves || 0) / (analysis.analysis?.total_leaves || 1) * 100).toFixed(1)}%)`}
            left={(props) => <List.Icon {...props} icon="alert-circle" color="#EF4444" />}
            titleStyle={styles.listItemTitle}
            descriptionStyle={[styles.listItemDescription, { color: '#EF4444' }]}
          />
        </Card.Content>
      </Card>

      {analysis.analysis?.diseases_detected && analysis.analysis.diseases_detected.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Diseases Detected
            </Text>
            {analysis.analysis.diseases_detected.map((detection: any, index: number) => (
              <View key={index} style={styles.diseaseItem}>
                <View style={styles.diseaseInfo}>
                  <Text variant="bodyMedium" style={styles.diseaseName}>
                    {detection.disease}
                  </Text>
                  <Text variant="bodySmall" style={styles.severityText}>
                    Severity: {detection.severity}
                  </Text>
                </View>
                <Chip 
                  compact 
                  style={[
                    styles.confidenceChip,
                    { backgroundColor: detection.confidence > 0.8 ? '#FEE2E2' : '#FEF3C7' }
                  ]}
                >
                  {(detection.confidence * 100).toFixed(0)}%
                </Chip>
              </View>
            ))}
          </Card.Content>
        </Card>
      )}

      {analysis.analysis?.recommendations && analysis.analysis.recommendations.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Treatment Recommendations
            </Text>
            {analysis.analysis.recommendations.map((rec, index) => (
              <View key={index} style={styles.recommendation}>
                <Text variant="bodyMedium">• {rec}</Text>
              </View>
            ))}
          </Card.Content>
        </Card>
      )}

      <View style={styles.actions}>
        <Button
          mode="contained"
          onPress={() => navigation.navigate('CoffeeLeaves' as never)}
          style={styles.button}
        >
          Analyze Another Image
        </Button>
      </View>

      <ImageViewer
        visible={imageViewerVisible}
        imageUri={analysis?.image_url || ''}
        onClose={() => setImageViewerVisible(false)}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 16,
    color: '#6B7280',
  },
  header: {
    padding: 20,
    backgroundColor: 'white',
    marginBottom: 16,
  },
  subtitle: {
    color: '#6B7280',
    marginTop: 4,
  },
  card: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  image: {
    height: 200,
  },
  imageOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    padding: 8,
    alignItems: 'center',
  },
  tapToViewText: {
    color: 'white',
    fontSize: 12,
  },
  scoreCard: {
    backgroundColor: '#F9FAFB',
  },
  scoreContainer: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  scoreCircle: {
    width: 90,
    height: 90,
    borderRadius: 45,
    borderWidth: 3,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  score: {
    fontWeight: 'bold',
  },
  scoreLabel: {
    color: '#6B7280',
    marginTop: 8,
  },
  qualityIndicator: {
    width: '80%',
    height: 8,
    marginTop: 16,
    position: 'relative',
  },
  qualityBar: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    borderRadius: 4,
  },
  qualityBarFill: {
    position: 'absolute',
    height: '100%',
    borderRadius: 4,
  },
  sectionTitle: {
    marginBottom: 16,
    color: '#374151',
  },
  listItemTitle: {
    fontWeight: '500',
    color: '#374151',
  },
  listItemDescription: {
    fontSize: 14,
    color: '#6B7280',
  },
  diseaseItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  diseaseInfo: {
    flex: 1,
  },
  diseaseName: {
    fontWeight: '500',
    color: '#374151',
  },
  severityText: {
    color: '#6B7280',
    marginTop: 4,
  },
  confidenceChip: {
    marginLeft: 12,
  },
  recommendation: {
    marginBottom: 8,
  },
  actions: {
    padding: 16,
  },
  button: {
    marginBottom: 12,
  },
});