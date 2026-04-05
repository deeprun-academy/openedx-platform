/* global gettext */
/* eslint react/no-array-index-key: 0 */

import PropTypes from 'prop-types';
import React from 'react';
// eslint-disable-next-line no-unused-vars
import ReactDOM from 'react-dom';

// DeepRun: Delete a course via our custom API, then reload to refresh the list.
function handleDeleteCourse(courseKey, displayName) {
    // eslint-disable-next-line no-alert
    if (!window.confirm(gettext('Delete course "') + displayName + gettext('"? This cannot be undone.'))) {
        return;
    }
    const xhr = new XMLHttpRequest();
    xhr.open('DELETE', '/api/deeprun/v1/course/' + courseKey, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            window.location.reload();
        } else {
            // eslint-disable-next-line no-alert
            window.alert(gettext('Failed to delete course: ') + xhr.status + ' ' + xhr.responseText);
        }
    };
    xhr.onerror = function() {
        // eslint-disable-next-line no-alert
        window.alert(gettext('Network error while deleting course.'));
    };
    xhr.send();
}

// eslint-disable-next-line import/prefer-default-export
export function CourseOrLibraryListing(props) {
    // eslint-disable-next-line prefer-destructuring
    const linkClass = props.linkClass;
    // eslint-disable-next-line prefer-destructuring
    const idBase = props.idBase;

    const renderCourseMetadata = (item, i) => (
        <div>
            <h3 className="course-title" id={`title-${idBase}-${i}`}>{item.display_name}</h3>
            <div className="course-metadata">
                <span className="course-org metadata-item">
                    <span className="label">{gettext('Organization:')}</span>
                    <span className="value">{item.org}</span>
                </span>
                <span className="course-num metadata-item">
                    <span className="label">{gettext('Course Number:')}</span>
                    <span className="value">{item.number}</span>
                </span>
                { item.run
            && (
                <span className="course-run metadata-item">
                    <span className="label">{gettext('Course Run:')}</span>
                    <span className="value">{item.run}</span>
                </span>
            )}
                { item.can_edit === false
            && <span className="extra-metadata">{gettext('(Read-only)')}</span>}
            </div>
        </div>
    );

    return (
        <ul className="list-courses">
            {
                props.items.map((item, i) => (
                    <li key={i} className="course-item" data-course-key={item.course_key}>
                        {item.url
                            ? (
                                <a className={linkClass} href={item.url}>
                                    {renderCourseMetadata(item, i)}
                                </a>
                            )
                            : renderCourseMetadata(item, i)}
                        { item.course_key
              && (
                  <ul className="item-actions course-actions">
                      <li className="action action-delete">
                          <button
                              type="button"
                              className="button delete-button"
                              aria-labelledby={`delete-${idBase}-${i} title-${idBase}-${i}`}
                              id={`delete-${idBase}-${i}`}
                              onClick={() => handleDeleteCourse(item.course_key, item.display_name)}
                          >{gettext('Delete')}
                          </button>
                      </li>
                  </ul>
              )}
                    </li>
                ))
            }
        </ul>
    );
}

CourseOrLibraryListing.propTypes = {
    allowReruns: PropTypes.bool.isRequired,
    idBase: PropTypes.string.isRequired,
    // eslint-disable-next-line react/forbid-prop-types
    items: PropTypes.arrayOf(PropTypes.object).isRequired,
    linkClass: PropTypes.string.isRequired,
};
