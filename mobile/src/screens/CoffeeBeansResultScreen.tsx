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
import { useGetCoffeeBeansAnalysisQuery } from '../services/coffeeBeansApi';
import ImageViewer from '../components/ImageViewer';

export default function CoffeeBeansResultScreen() {
  const route = useRoute<any>();
  const navigation = useNavigation();
  const { analysisId, analysisData } = route.params;
  const [imageViewerVisible, setImageViewerVisible] = useState(false);
  
  // Debug: Log received parameters
  console.log('🔍 CoffeeBeansResultScreen - params:', {
    analysisId,
    hasAnalysisData: !!analysisData,
    analysisDataFields: analysisData ? Object.keys(analysisData) : [],
  });
  
  // Skip fetching data since we pass it directly via navigation
  // const { data: analysis, isLoading, error } = useGetCoffeeBeansAnalysisQuery(analysisId, {
  //   skip: true, // Always skip - we use passed data instead
  // });
  const analysis = null; // Not used since we use analysisData
  const isLoading = false;
  const error = null;

  // Handle missing analysisId or analysisData
  if (!analysisId || !analysisData) {
    return (
      <View style={styles.centerContainer}>
        <Text variant="bodyLarge">
          {!analysisId ? "Analysis ID is missing" : "Analysis data is missing"}
        </Text>
        <Button mode="contained" onPress={() => navigation.goBack()} style={styles.button}>
          Go Back
        </Button>
      </View>
    );
  }

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

  // Use passed data if available, otherwise use fetched data
  const displayAnalysis = analysisData || analysis;

  if (error || (!displayAnalysis && !isLoading)) {
    return (
      <View style={styles.centerContainer}>
        <Text variant="bodyLarge">Failed to load analysis results</Text>
        <Button mode="contained" onPress={() => navigation.goBack()} style={styles.button}>
          Go Back
        </Button>
      </View>
    );
  }

  // Add safety check for analysis data structure
  if (!displayAnalysis?.analysis) {
    return (
      <View style={styles.centerContainer}>
        <Text variant="bodyLarge">Invalid analysis data format</Text>
        <Button mode="contained" onPress={() => navigation.goBack()} style={styles.button}>
          Go Back
        </Button>
      </View>
    );
  }

  const qualityScore = displayAnalysis.analysis?.quality_score || 0;
  const scoreColor = qualityScore >= 80 ? '#10B981' : qualityScore >= 60 ? '#F59E0B' : '#EF4444';

  return (
    <ScrollView style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <Text variant="titleLarge">Analysis Results</Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Coffee Beans Quality Report
        </Text>
      </Surface>

      {displayAnalysis.image_url && (
        <TouchableOpacity onPress={() => setImageViewerVisible(true)}>
          <Card style={styles.card}>
            <Card.Cover source={{ uri: displayAnalysis.image_url }} style={styles.image} />
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
              <Text variant="displaySmall" style={[styles.score, { color: scoreColor }]}>
                {qualityScore.toFixed(1)}%
              </Text>
            </View>
            <Text variant="titleMedium" style={styles.scoreLabel}>
              Quality Score
            </Text>
            <View style={styles.qualityIndicator}>
              <View style={[styles.qualityBar, { backgroundColor: '#E5E7EB' }]} />
              <View 
                style={[
                  styles.qualityBarFill, 
                  { 
                    backgroundColor: scoreColor,
                    width: `${qualityScore}%` 
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
            Bean Analysis
          </Text>
          <List.Item
            title="Total Beans"
            description={`${displayAnalysis.analysis?.total_beans || 0} beans detected`}
            left={(props) => <List.Icon {...props} icon="coffee" />}
            titleStyle={styles.listItemTitle}
            descriptionStyle={styles.listItemDescription}
          />
          <List.Item
            title="Good Beans"
            description={`${displayAnalysis.analysis?.good_beans || 0} beans (${((displayAnalysis.analysis?.good_beans || 0) / (displayAnalysis.analysis?.total_beans || 1) * 100).toFixed(1)}%)`}
            left={(props) => <List.Icon {...props} icon="check-circle" color="#10B981" />}
            titleStyle={styles.listItemTitle}
            descriptionStyle={[styles.listItemDescription, { color: '#10B981' }]}
          />
          <List.Item
            title="Defect Beans"
            description={`${displayAnalysis.analysis?.defect_beans || 0} beans (${((displayAnalysis.analysis?.defect_beans || 0) / (displayAnalysis.analysis?.total_beans || 1) * 100).toFixed(1)}%)`}
            left={(props) => <List.Icon {...props} icon="alert-circle" color="#EF4444" />}
            titleStyle={styles.listItemTitle}
            descriptionStyle={[styles.listItemDescription, { color: '#EF4444' }]}
          />
        </Card.Content>
      </Card>

      {displayAnalysis.analysis?.defects_breakdown && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Defects Breakdown
            </Text>
            {Object.entries(displayAnalysis.analysis.defects_breakdown).map(([defect, count]) => (
              <View key={defect} style={styles.defectItem}>
                <Text variant="bodyMedium">{defect}</Text>
                <Chip compact>{count as number}</Chip>
              </View>
            ))}
          </Card.Content>
        </Card>
      )}

      {displayAnalysis.analysis?.recommendations && displayAnalysis.analysis.recommendations.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Recommendations
            </Text>
            {displayAnalysis.analysis.recommendations.map((rec, index) => (
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
          onPress={() => navigation.navigate('CoffeeBeans' as never)}
          style={styles.button}
        >
          Analyze Another Image
        </Button>
      </View>

      <ImageViewer
        visible={imageViewerVisible}
        imageUri={displayAnalysis?.image_url || ''}
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
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 4,
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
  defectItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
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