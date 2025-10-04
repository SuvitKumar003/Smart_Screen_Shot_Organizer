import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

class FileManager:
    def __init__(self):
        self.base_output_dir = "organized"
        self.temp_zip_dir = "temp_zip"
        
        # Create directories if they don't exist
        os.makedirs(self.base_output_dir, exist_ok=True)
        os.makedirs(self.temp_zip_dir, exist_ok=True)
    
    def clean_directory(self, directory):
        """Remove all files in a directory"""
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory, exist_ok=True)
    
    def organize_files(self, extracted_data, organized_results):
        """
        Organize files into folders based on clustering results
        
        Args:
            extracted_data: Dict of {filename: {'text': str, 'file': file}}
            organized_results: Results from clustering engine
            
        Returns:
            str: Path to the organized directory
        """
        # Create timestamp for this organization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(self.base_output_dir, f"organized_{timestamp}")
        
        # Clean and create output directory
        self.clean_directory(output_dir)
        
        # Organize matched files
        for tag, filenames in organized_results['matched'].items():
            if filenames:
                tag_dir = os.path.join(output_dir, tag)
                os.makedirs(tag_dir, exist_ok=True)
                
                for filename in filenames:
                    self._save_file(
                        extracted_data[filename]['file'],
                        tag_dir,
                        filename
                    )
        
        # Organize clustered files
        for cluster_name, filenames in organized_results['clustered'].items():
            cluster_dir = os.path.join(output_dir, cluster_name)
            os.makedirs(cluster_dir, exist_ok=True)
            
            for filename in filenames:
                self._save_file(
                    extracted_data[filename]['file'],
                    cluster_dir,
                    filename
                )
        
        return output_dir
    
    def _save_file(self, file_obj, directory, filename):
        """Save uploaded file to directory"""
        file_obj.seek(0)
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'wb') as f:
            f.write(file_obj.read())
    
    def create_zip(self, organized_dir):
        """
        Create a ZIP file of the organized directory
        
        Args:
            organized_dir: Path to organized directory
            
        Returns:
            str: Path to created ZIP file
        """
        # Create ZIP filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"organized_screenshots_{timestamp}.zip"
        zip_path = os.path.join(self.temp_zip_dir, zip_filename)
        
        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(organized_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Get relative path for ZIP
                    arcname = os.path.relpath(file_path, organized_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    def get_statistics(self, organized_results):
        """
        Generate statistics about organization
        
        Args:
            organized_results: Results from clustering engine
            
        Returns:
            dict: Statistics
        """
        stats = {
            'total_matched': 0,
            'total_clustered': 0,
            'tags_used': 0,
            'clusters_created': 0,
            'tag_distribution': {},
            'cluster_distribution': {}
        }
        
        # Count matched files
        for tag, filenames in organized_results['matched'].items():
            count = len(filenames)
            stats['total_matched'] += count
            if count > 0:
                stats['tags_used'] += 1
                stats['tag_distribution'][tag] = count
        
        # Count clustered files
        for cluster, filenames in organized_results['clustered'].items():
            count = len(filenames)
            stats['total_clustered'] += count
            stats['clusters_created'] += 1
            stats['cluster_distribution'][cluster] = count
        
        stats['total_images'] = stats['total_matched'] + stats['total_clustered']
        
        return stats
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_zip_dir):
            for file in os.listdir(self.temp_zip_dir):
                file_path = os.path.join(self.temp_zip_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")