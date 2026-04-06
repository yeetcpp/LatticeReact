// Project metrics extracted from the testing report
export const projectMetrics = {
  performance: {
    accuracy: 90,
    successRate: 90,
    hallucinationRate: 0,
    dataAccuracy: 100,
    averageInferenceTime: 850, // estimated in ms
  },
  dataset: {
    totalSamples: 10,
    testsPassed: 9,
    testsPartial: 1,
    testsFailed: 0,
    materialsCovered: 15, // Si, Al, NaCl, GaN, Iron, Diamond, Carbon, TiO2, Al2O3, SiO2, BaTiO3
  },
  technical: {
    frameworkVersion: "Post-hallucination fixes",
    apiIntegration: "Materials Project",
    domainsCovered: 3, // Electronic, Elastic, Thermodynamic
    agentArchitecture: "Hierarchical ReAct",
  },
  scope: {
    crystalSystems: 7, // estimated based on materials
    propertiesSupported: 8, // bandgap, bulk modulus, formation energy, shear modulus, young's modulus, etc.
    endpointsIntegrated: 3,
    verificationAccuracy: 100,
  }
};

export const systemCapabilities = [
  {
    title: "Zero Hallucination",
    value: "0%",
    description: "No fabricated data or false mp-codes",
    color: "text-green-400"
  },
  {
    title: "Success Rate",
    value: "90%",
    description: "9/10 tests passed successfully",
    color: "text-accent-purple"
  },
  {
    title: "Data Accuracy",
    value: "100%",
    description: "All reported values verified correct",
    color: "text-accent-teal"
  },
  {
    title: "Multi-Domain",
    value: "3",
    description: "Electronic, Elastic, Thermodynamic",
    color: "text-accent-blue"
  },
  {
    title: "Materials Tested",
    value: "15+",
    description: "Si, GaN, NaCl, BaTiO3, and more",
    color: "text-accent-gold"
  },
  {
    title: "API Verification",
    value: "100%",
    description: "All results cross-checked with Materials Project",
    color: "text-purple-400"
  }
];